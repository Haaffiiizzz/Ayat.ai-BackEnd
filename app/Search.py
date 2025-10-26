import json
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
import os
from functools import lru_cache
from .main2 import TranscribeAudio, LoadDataSet, ProcessMatches
from .rerank import Rerank
load_dotenv()
apiKey = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=apiKey)

# Cached, read-only data loaded at startup
cachedEmbeddings = None          # np.memmap/ndarray (N, D) float32
cachedRowNorms = None            # np.ndarray (N,) float32
cachedRowToVerseId = None        # dict[int, str]
cachedVerseById = None           # dict[str, dict]

def cosineSimilarity(queryVector, embeddingsMatrix, rowNorms):
    """Cosine similarity using precomputed row norms.

    Args:
        queryVector: 1D float32 array for the query embedding.
        embeddingsMatrix: 2D float32 array/memmap of embeddings.
        rowNorms: 1D float32 array of precomputed L2 norms per row.
    Returns:
        1D float32 array of cosine similarity scores.
    """
    qNorm = float(np.linalg.norm(queryVector) + 1e-9)
    dots = embeddingsMatrix @ queryVector
    return dots / ((rowNorms + 1e-9) * qNorm)

@lru_cache(maxsize=256)
def embedQueryVectorCached(queryText: str, modelName: str):
    """LRU-cached OpenAI embedding for a query string.

    Caches by (queryText, modelName) to reduce repeated network calls.
    Returns a float32 numpy array.
    """
    response = client.embeddings.create(model=modelName, input=[queryText])
    return np.array(response.data[0].embedding, dtype=np.float32)

def InitSearchCache(
    embeddingsPath: str = "app/data/embeddings.npy",
    indexPath: str = "app/data/index.json",
    versesPath: str = "app/data/Verses.json",
):
    """Preload embeddings, row norms, index map, and verses into module cache.

    Called on app startup so requests avoid repeated disk IO and preprocessing.
    Embeddings are memory-mapped for low RSS with fast matmul.
    """
    global cachedEmbeddings, cachedRowNorms, cachedRowToVerseId, cachedVerseById

    embeddingsMatrix = np.load(embeddingsPath, mmap_mode="r")
    if embeddingsMatrix.dtype != np.float32:
        embeddingsMatrix = embeddingsMatrix.astype(np.float32)

    rowNorms = np.linalg.norm(embeddingsMatrix, axis=1).astype(np.float32)

    with open(indexPath, "r", encoding="utf-8") as f:
        indexMeta = json.load(f)
    rowToVerseId = {rowIdx: verseId for verseId, rowIdx in indexMeta["index"].items()}

    with open(versesPath, "r", encoding="utf-8") as f:
        versesData = json.load(f)
    verseById = {v["VerseID"]: v for v in versesData}

    cachedEmbeddings = embeddingsMatrix
    cachedRowNorms = rowNorms
    cachedRowToVerseId = rowToVerseId
    cachedVerseById = verseById

def SearchVerses(
    queryText,
    embeddingsPath="app/data/embeddings.npy",
    indexPath="app/data/index.json",
    versesPath="app/data/Verses.json",
    minSimilarity=0.2,
    topK_candidates=100,
    topN_final=100,
    client=client,
    modelName="text-embedding-3-large",
):
    """Search verses using cached data and LRU-cached query embeddings.

    Ensures caches are loaded, embeds the query via LRU cache, computes cosine
    similarities using precomputed row norms, filters by `minSimilarity`, and
    reranks batched via cross-encoder.
    """
    global cachedEmbeddings, cachedRowNorms, cachedRowToVerseId, cachedVerseById
    if cachedEmbeddings is None or cachedRowNorms is None or cachedRowToVerseId is None or cachedVerseById is None:
        InitSearchCache(embeddingsPath, indexPath, versesPath)

    embeddingsMatrix = cachedEmbeddings
    rowNorms = cachedRowNorms
    rowToVerseId = cachedRowToVerseId
    verseById = cachedVerseById

    queryVector = embedQueryVectorCached(queryText, modelName)
    similarities = cosineSimilarity(queryVector, embeddingsMatrix, rowNorms)

    # Decide candidate pool: either all or topK
    if topK_candidates is None:
        topIdx = np.arange(similarities.shape[0])
    else:
        k = min(int(topK_candidates), similarities.shape[0])
        if k <= 0:
            return []
        topIdx = np.argpartition(-similarities, kth=k - 1)[:k]

    # Build initial candidate list filtered by minSimilarity
    results = []
    for rowIdx in topIdx:
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
    """Transcribe audio and return best fuzzy-matched verse from the dataset."""
    transcribedAudio = TranscribeAudio(audioFile, model)
    dataset = LoadDataSet("app/data/Verses.json")
    matches = ProcessMatches(transcribedAudio, dataset)
    if not matches:
        return None
    bestMatch = matches[0]
    verseIndex = bestMatch[2]
    bestMatchDict = dataset[verseIndex]
    return bestMatchDict
