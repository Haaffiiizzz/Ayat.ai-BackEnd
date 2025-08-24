import numpy as np
import pandas as pd
from pathlib import Path

from sentence_transformers import SentenceTransformer

from sklearn.decomposition import PCA
from sklearn.metrics import DistanceMetric

import matplotlib.pyplot as plt
import matplotlib as mpl

df = pd.read_json("app/data/Verses.json")
df["VerseEnglish"] = df["VerseEnglish"].fillna("").str.strip()


model = SentenceTransformer("all-MiniLM-L6-v2")

# embeddings = model.encode(
#     df["VerseEnglish"].tolist(),
#     batch_size=64,
#     normalize_embeddings=True,
#     show_progress_bar=True
# )
# embeddings = np.asarray(embeddings)  

# embeddingsNumpyPath = Path("app/data/verses_emb_minilm_cosine.npy")
# np.save(embeddingsNumpyPath, embeddings)
# print(f"Saved embeddings to {embeddingsNumpyPath}")


# # 2) optional: .npz with ids to avoid mismatch later
# embeddingsNpzPath = Path("app/data/verses_emb_minilm_cosine.npz")  
# verseIds = df["VerseID"].to_numpy()
# np.savez_compressed(embeddingsNpzPath, emb=embeddings, verseIds=verseIds)
# print(f"Saved embeddings + ids to {embeddingsNpzPath}")

embeddings = np.load("app/data/verses_emb_minilm_cosine.npy")


def search(query: str, k: int = 10):
    q = model.encode(query, normalize_embeddings=True)
    scores = embeddings @ q  # cosine similarity
    topk = np.argsort(-scores)[:k]
    results = df.iloc[topk][[
        "VerseID", "SurahNumber", "VerseNumber", "SurahNameEnglish", "VerseEnglish"
    ]].copy()
    results["score"] = scores[topk]
    return results



if __name__ == "__main__":
    # quick test search
    demo = search("taking care of parents", k=10)
    for idx, res in demo.iterrows():
        print(res)
        print("\n")
