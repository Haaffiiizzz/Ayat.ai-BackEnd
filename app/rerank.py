from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("cross-encoder/ms-marco-MiniLM-L-6-v2")
model = AutoModelForSequenceClassification.from_pretrained("cross-encoder/ms-marco-MiniLM-L-6-v2")

def Rerank(query, results, topN=None):
    """
    Re-rank results using a cross-encoder.
    results: list of dicts with "verseEnglish"
    topN: optional number of top reranked results to keep
    """
    inputs = tokenizer(
        [(query, r["VerseObject"]["VerseEnglish"]) for r in results],
        padding=True,
        truncation=True,
        return_tensors="pt"
    )

    with torch.no_grad():
        scores = model(**inputs).logits.squeeze(-1)

    # attach scores back
    for r, s in zip(results, scores):
        r["relevanceScore"] = float(s)

    # sort by new score
    results = sorted(results, key=lambda x: -x["relevanceScore"])

    if topN:
        results = results[:topN]

    return results
