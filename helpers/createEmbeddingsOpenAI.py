# file: build_embeddings.py
import os
import json
import time
from datetime import datetime
from typing import List, Dict

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

# 0) env and client
load_dotenv()
apiKey = os.getenv("OPENAI_API_KEY")
if not apiKey:
    raise RuntimeError("OPENAI_API_KEY not found in environment. Put it in .env")

client = OpenAI(api_key=apiKey)

MODEL_NAME = "text-embedding-3-large"   # 3072 dims
BATCH_SIZE = 128                        # safe default

def chunk(items: List, size: int):
    for i in range(0, len(items), size):
        yield items[i:i+size]

def embedBatch(texts: List[str]) -> List[List[float]]:
    resp = client.embeddings.create(model=MODEL_NAME, input=texts)
    return [d.embedding for d in resp.data]

def loadVersesFromJsonArray(jsonPath: str) -> List[Dict]:
    with open(jsonPath, "r", encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Input JSON must be a list of verse objects")
        return data

def buildEmbeddings(
    inputPath: str = "app/data/Verses.json",
    outVecPath: str = "embeddings.npy",
    outIndexPath: str = "index.json",
    textField: str = "VerseEnglish",   # use English text for embeddings
    idField: str = "VerseID"
):
    # 1) load verses
    verses = loadVersesFromJsonArray(inputPath)
    if not verses:
        raise ValueError("No verses found in input JSON")

    # 2) collect ids and texts
    verseIds = []
    texts = []
    for v in verses:
        vid = v.get(idField)
        txt = v.get(textField)
        if not vid or not txt:
            # skip incomplete rows but warn
            print(f"Skipping row missing {idField} or {textField}: {v}")
            continue
        verseIds.append(vid)
        texts.append(txt)

    if not texts:
        raise ValueError(f"No usable verses with field {textField}")

    # 3) embed in batches
    vectors = []
    for group in chunk(texts, BATCH_SIZE):
        try:
            vecs = embedBatch(group)
        except Exception as e:
            print(f"OpenAI error: {e}. Retrying once after short sleep.")
            time.sleep(2.0)
            vecs = embedBatch(group)
        vectors.extend(vecs)

    # 4) save npy
    arr = np.asarray(vectors, dtype=np.float32)  # shape (N, 3072)
    np.save(outVecPath, arr)

    # 5) save index.json
    indexMap = {vid: i for i, vid in enumerate(verseIds)}
    meta = {
        "model": MODEL_NAME,
        "dim": int(arr.shape[1]),
        "count": int(arr.shape[0]),
        "idField": idField,
        "textField": textField,
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "index": indexMap
    }
    with open(outIndexPath, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)

    print(f"Saved {arr.shape[0]} vectors to {outVecPath}")
    print(f"Wrote index to {outIndexPath}")
    print("Done.")

if __name__ == "__main__":
    # change paths if your files are elsewhere
    buildEmbeddings(
        inputPath="app/data/Verses.json",
        outVecPath="embeddings.npy",
        outIndexPath="index.json",
        textField="VerseEnglish",   # or "VerseWithoutHarakat" if you want Arabic without diacritics
        idField="VerseID"
    )
