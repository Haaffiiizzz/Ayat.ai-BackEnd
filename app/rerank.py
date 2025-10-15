from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Lazy-load model/tokenizer to avoid heavy import-time cost
_tokenizer = None
_model = None

def _get_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        # Limit CPU thread usage to avoid system freeze under load
        try:
            torch.set_num_threads(1)
            torch.set_num_interop_threads(1)
        except Exception:
            pass

        _tokenizer = AutoTokenizer.from_pretrained("cross-encoder/ms-marco-MiniLM-L-6-v2")
        _model = AutoModelForSequenceClassification.from_pretrained("cross-encoder/ms-marco-MiniLM-L-6-v2")
        _model.eval()
    return _tokenizer, _model

def Rerank(query, results, topN=None, batch_size=16):
    """
    Re-rank results using a cross-encoder.
    - results: list of dicts each containing VerseObject["VerseEnglish"]
    - topN: optional number of top reranked results to keep
    - batch_size: limit per-forward pass to control memory/CPU
    """
    if not results:
        return results

    tokenizer, model = _get_model()

    # Compute scores in mini-batches to avoid huge allocations
    texts = [r["VerseObject"]["VerseEnglish"] for r in results]
    all_scores = []
    for start in range(0, len(texts), batch_size):
        batch_pairs = [(query, t) for t in texts[start:start + batch_size]]
        inputs = tokenizer(
            batch_pairs,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )
        with torch.no_grad():
            logits = model(**inputs).logits.squeeze(-1)
        all_scores.extend([float(s) for s in logits])

    for r, s in zip(results, all_scores):
        r["relevanceScore"] = s

    results = sorted(results, key=lambda x: -x["relevanceScore"])
    if topN:
        results = results[:topN]
    return results

def preload_reranker():
    """
    Preload tokenizer and model into memory at app startup to avoid
    first-request latency. Safe to call multiple times.
    """
    _get_model()
