import json
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
import os

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

def searchVerses(queryText,
                 embeddingsPath="app/data/embeddings.npy",
                 indexPath="app/data/index.json",
                 versesPath="app/data/Verses.json",
                 k=10,
                 client=client,
                 modelName="text-embedding-3-large"):
    # load embeddings
    embeddingsMatrix = np.load(embeddingsPath)

    # load index
    with open(indexPath, "r", encoding="utf-8") as f:
        indexMeta = json.load(f)
    rowToVerseId = {rowIdx: verseId for verseId, rowIdx in indexMeta["index"].items()}

    # embed query
    queryVector = embedQueryText(queryText, client, modelName)

    # compute similarities
    similarities = cosineSimilarity(queryVector, embeddingsMatrix)

    # get top-k row indices
    topRowIndices = np.argsort(-similarities)[:k]
    results = []

    # load verses into a dict for quick lookup
    with open(versesPath, "r", encoding="utf-8") as f:
        versesData = json.load(f)
    verseById = {v["VerseID"]: v for v in versesData}

    # build results
    for rowIdx in topRowIndices:
        verseId = rowToVerseId[rowIdx]
        verseObj = verseById[verseId]
        results.append({
            "verseId": verseId,
            "similarity": float(similarities[rowIdx]),
            "verseEnglish": verseObj.get("VerseEnglish"),
            "verseArabic": verseObj.get("VerseWithoutHarakat"),
            "tags": verseObj.get("tags", [])
        })

    return results