import json
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
import os
from .main2 import TranscribeAudio, LoadDataSet, ProcessMatches
from .rerank import Rerank
load_dotenv()
apiKey = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=apiKey)

def cosineSimilarity(queryVector, embeddingsMatrix):
    """
    Compute cosine similarity without materializing a second NxD array.
    This reduces peak memory usage significantly.
    """
    q_norm = float(np.linalg.norm(queryVector) + 1e-9)
    row_norms = np.linalg.norm(embeddingsMatrix, axis=1) + 1e-9  # (N,)
    dots = embeddingsMatrix @ queryVector  # (N,)
    return dots / (row_norms * q_norm)

def embedQueryText(queryText: str, client, modelName: str):
    response = client.embeddings.create(model=modelName, input=[queryText])
    return np.array(response.data[0].embedding, dtype=np.float32)

def SearchVerses(
    queryText,
    embeddingsPath="app/data/embeddings.npy",
    indexPath="app/data/index.json",
    versesPath="app/data/Verses.json",
    minSimilarity=0.2,
    topK_candidates=300,
    topN_final=None,
    client=client,
    modelName="text-embedding-3-large",
):
    """
    Embed query, compute cosine similarity over precomputed embeddings, take topK,
    then cross-encoder rerank in batches to avoid memory/CPU spikes.
    """
    # Load embeddings (memory-mapped to reduce peak RAM; matmul will stream)
    embeddingsMatrix = np.load(embeddingsPath, mmap_mode="r")

    with open(indexPath, "r", encoding="utf-8") as f:
        indexMeta = json.load(f)
    rowToVerseId = {rowIdx: verseId for verseId, rowIdx in indexMeta["index"].items()}

    queryVector = embedQueryText(queryText, client, modelName)
    similarities = cosineSimilarity(queryVector, embeddingsMatrix)

    # Decide candidate pool: either all or topK
    if topK_candidates is None:
        top_idx = np.arange(similarities.shape[0])
    else:
        k = min(int(topK_candidates), similarities.shape[0])
        if k <= 0:
            return []
        top_idx = np.argpartition(-similarities, kth=k - 1)[:k]

    with open(versesPath, "r", encoding="utf-8") as f:
        versesData = json.load(f)
    verseById = {v["VerseID"]: v for v in versesData}

    # Build initial candidate list filtered by minSimilarity
    results = []
    for rowIdx in top_idx:
        score = float(similarities[rowIdx])
        if score < minSimilarity:
            continue
        verseId = rowToVerseId[rowIdx]
        verseObj = verseById[verseId]
        results.append({
            "VerseID": verseId,
            "similarity": score,
            "VerseObject": verseObj,
        })

    # Sort by similarity prior to reranking to keep best first
    results.sort(key=lambda x: -x["similarity"])

    # Cross-encoder reranking with batching (implemented in Rerank)
    rerankedResult = Rerank(queryText, results, topN=topN_final, batch_size=16)
    return rerankedResult


def SearchAudio(audioFile, model):
    transcribedAudio = TranscribeAudio(audioFile, model)
    dataset = LoadDataSet("app/data/Verses.json")
    
    matches = ProcessMatches(transcribedAudio, dataset)
    if matches:
        
        bestMatch = matches[0]
        verseIndex = bestMatch[2]
        bestMatchDict = dataset[verseIndex] #bestMatch[2] is index of the best match dict in the dataaset list
        return bestMatchDict
    else:
        return None
