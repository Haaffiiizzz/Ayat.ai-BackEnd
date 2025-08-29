import json, time
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()
MODEL_NAME = "text-embedding-3-large"

def embedBatch(texts):
    resp = client.embeddings.create(model=MODEL_NAME, input=texts)
    return [d.embedding for d in resp.data]

def buildEmbeddings(versesPath="verses.jsonl", outVecPath="embeddings.npy", outIndexPath="index.json"):
    verses = []
    with open(versesPath, "r", encoding="utf-8") as f:
        for line in f:
            verses.append(json.loads(line))

    verseIds = [v["VerseID"] for v in verses]
    texts = [v["verseText"] if "verseText" in v else v["VerseEnglish"] for v in verses]

    vectors = []
    batchSize = 128
    for i in range(0, len(texts), batchSize):
        batch = texts[i:i+batchSize]
        resp = embedBatch(batch)
        vectors.extend(resp)

    arr = np.asarray(vectors, dtype=np.float32)  # shape (N, 3072)
    np.save(outVecPath, arr)

    index = {vid: i for i, vid in enumerate(verseIds)}
    with open(outIndexPath, "w", encoding="utf-8") as f:
        json.dump({"model": MODEL_NAME, "dim": arr.shape[1], "index": index}, f)

    print(f"Saved {arr.shape[0]} embeddings to {outVecPath}")
