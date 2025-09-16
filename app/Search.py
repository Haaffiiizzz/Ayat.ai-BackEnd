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
    # normalize
    qNorm = queryVector / (np.linalg.norm(queryVector) + 1e-9)
    mNorm = embeddingsMatrix / (np.linalg.norm(embeddingsMatrix, axis=1, keepdims=True) + 1e-9)
    return mNorm @ qNorm  # (N,)

def embedQueryText(queryText: str, client, modelName: str):
    response = client.embeddings.create(model=modelName, input=[queryText])
    return np.array(response.data[0].embedding, dtype=np.float32)

def SearchVerses(queryText,
                 embeddingsPath="app/data/embeddings.npy",
                 indexPath="app/data/index.json",
                 versesPath="app/data/Verses.json",
                 minSimilarity=0.2,
                 client=client,
                 modelName="text-embedding-3-large"):

    embeddingsMatrix = np.load(embeddingsPath)

    with open(indexPath, "r", encoding="utf-8") as f:
        indexMeta = json.load(f)
    rowToVerseId = {rowIdx: verseId for verseId, rowIdx in indexMeta["index"].items()}

    queryVector = embedQueryText(queryText, client, modelName)

    similarities = cosineSimilarity(queryVector, embeddingsMatrix)

    with open(versesPath, "r", encoding="utf-8") as f:
        versesData = json.load(f)
    verseById = {v["VerseID"]: v for v in versesData}

    results = []
    for rowIdx, score in enumerate(similarities):
        if score >= minSimilarity:  # 👈 keep everything above threshold
            verseId = rowToVerseId[rowIdx]
            verseObj = verseById[verseId]
            results.append({
                "verseId": verseId,
                "similarity": float(score),
                "verseEnglish": verseObj.get("VerseEnglish"),
                "verseArabic": verseObj.get("VerseWithoutHarakat"),
                "tags": verseObj.get("tags", []),
                "VerseIndex": int(rowIdx)
            })

    # sort results from most similar to least similar
    results.sort(key=lambda x: -x["similarity"])
    
    rerankedResult = Rerank(queryText, results)
    return rerankedResult


def SearchAudio(audioFile):
    transcribedAudio = TranscribeAudio(audioFile)
    dataset = LoadDataSet("app/data/Verses.json")
    
    matches = ProcessMatches(transcribedAudio, dataset)
    if matches:
        
        bestMatch = matches[0]
        verseIndex = bestMatch[2]
        bestMatchDict = dataset[verseIndex] #bestMatch[2] is index of the best match dict in the dataaset list
        bestMatchDict["VerseIndex"] = verseIndex
        return bestMatchDict
    else:
        return None
