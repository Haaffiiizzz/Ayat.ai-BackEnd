import json, random, argparse, math, re
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import pandas as pd
import numpy as np
from rapidfuzz import fuzz, process

# -----------------------------
# Helpers
# -----------------------------
def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

def load_verses(verses_path: Path) -> pd.DataFrame:
    df = pd.read_json(verses_path)
    # Keep only what we need
    keep_cols = [c for c in ["VerseID", "VerseWithoutHarakat"] if c in df.columns]
    df = df[keep_cols].copy()
    df["VerseWithoutHarakat"] = df["VerseWithoutHarakat"].fillna("").astype(str)
    df["norm"] = df["VerseWithoutHarakat"].map(normalize_text)
    return df


def load_test_cases(test_path: Optional[Path]) -> Optional[List[Dict]]:
    if test_path is None or not test_path.exists():
        return None
    cases = []
    with test_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            cases.append(json.loads(line))
    return cases

def add_typo_noise(words: List[str], noise_prob=0.12) -> List[str]:
    # Light noise: drop, swap, or small char tweak
    def tweak_word(w: str) -> str:
        if len(w) <= 3:
            return w
        i = random.randint(0, len(w)-2)
        ops = random.choice(["drop", "swap"])
        if ops == "drop":
            return w[:i] + w[i+1:]
        else:
            return w[:i] + w[i+1] + w[i] + w[i+2:]
    out = []
    for w in words:
        if random.random() < noise_prob:
            out.append(tweak_word(w))
        else:
            out.append(w)
    return out

def synthesize_cases(df: pd.DataFrame, n_cases=200, min_span=3, max_span=8) -> List[Dict]:
    rng = random.Random(1337)
    cases = []
    for _ in range(n_cases):
        row = df.sample(1, random_state=rng.randint(0, 10**9)).iloc[0]
        verse_id = row["VerseID"]
        text = row["norm"]
        tokens = text.split()
        if len(tokens) < min_span:
            continue
        span = rng.randint(min_span, min(max_span, max(min_span, len(tokens))))
        start = rng.randint(0, max(0, len(tokens) - span))
        snippet_tokens = tokens[start:start+span]
        snippet_tokens = add_typo_noise(snippet_tokens, noise_prob=0.12)
        query = " ".join(snippet_tokens)
        cases.append({"query": query, "verseId": verse_id})
    return cases

# -----------------------------
# Matchers
# -----------------------------
def predict_exact_keyword(query: str, df: pd.DataFrame) -> Optional[str]:
    q = normalize_text(query)
    # Filter by substring presence
    mask = df["norm"].str.contains(re.escape(q), regex=True)
    if not mask.any():
        return None
    candidates = df[mask]
    # Prefer longest overlap (proxy for best match)
    overlaps = candidates["norm"].str.len()
    best_idx = overlaps.idxmax()
    return candidates.loc[best_idx, "VerseID"]

def predict_rapidfuzz(query: str, df: pd.DataFrame, threshold: int = 0) -> Optional[str]:
    q = normalize_text(query)
    # Compute best match
    # Using token_set_ratio is robust for reordering and partial overlap
    scores = df["norm"].map(lambda s: fuzz.token_set_ratio(q, s))
    best_idx = scores.idxmax()
    best_score = scores.loc[best_idx]
    if best_score < threshold:
        return None
    return df.loc[best_idx, "VerseID"]

# -----------------------------
# Evaluation
# -----------------------------
def evaluate(cases: List[Dict], df: pd.DataFrame, threshold: int = 0) -> Dict[str, float]:
    exact_correct = 0
    exact_total = 0

    rf_correct = 0
    rf_total = 0

    for ex in cases:
        q = ex["query"]
        true_id = ex["verseId"]

        # Exact
        pred_exact = predict_exact_keyword(q, df)
        if pred_exact is not None:
            exact_total += 1
            if pred_exact == true_id:
                exact_correct += 1

        # RapidFuzz
        pred_rf = predict_rapidfuzz(q, df, threshold=threshold)
        if pred_rf is not None:
            rf_total += 1
            if pred_rf == true_id:
                rf_correct += 1

    # Accuracy on answered queries; mismatch = 1 - accuracy
    exact_acc = (exact_correct / exact_total) if exact_total else 0.0
    rf_acc = (rf_correct / rf_total) if rf_total else 0.0

    return {
        "exact_answered": exact_total,
        "exact_correct": exact_correct,
        "exact_accuracy_at_1": round(exact_acc, 4),
        "exact_mismatch_rate": round(1 - exact_acc, 4) if exact_total else 1.0,

        "rapidfuzz_answered": rf_total,
        "rapidfuzz_correct": rf_correct,
        "rapidfuzz_accuracy_at_1": round(rf_acc, 4),
        "rapidfuzz_mismatch_rate": round(1 - rf_acc, 4) if rf_total else 1.0
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verses", type=str, default= "app/Verses.json", help="Path to Verses.json")
    parser.add_argument("--test", type=str, default=None, help="Optional path to test_cases.jsonl")
    parser.add_argument("--threshold", type=int, default=60, help="RapidFuzz minimum score to accept a match (0-100)")
    parser.add_argument("--n_synth", type=int, default=1000, help="Number of synthetic cases if no test file")
    args = parser.parse_args()

    df = load_verses(Path(args.verses))

    cases = load_test_cases(Path(args.test)) if args.test else None
    if not cases:
        print(f"[info] No labeled test set provided. Generating {args.n_synth} synthetic cases from VerseWithoutHarakat.")
        cases = synthesize_cases(df, n_cases=args.n_synth)

    report = evaluate(cases, df, threshold=args.threshold)

    print("\n=== Partial Recitation Evaluation ===")
    print(f"Total cases evaluated: {len(cases)}")
    print(f"RapidFuzz threshold: {args.threshold}\n")

    # Exact
    print("[Exact Keyword]")
    print(f" answered={report['exact_answered']}, correct={report['exact_correct']}")
    print(f" accuracy@1={report['exact_accuracy_at_1']:.4f}, mismatch_rate={report['exact_mismatch_rate']:.4f}\n")

    # RapidFuzz
    print("[RapidFuzz token_set_ratio]")
    print(f" answered={report['rapidfuzz_answered']}, correct={report['rapidfuzz_correct']}")
    print(f" accuracy@1={report['rapidfuzz_accuracy_at_1']:.4f}, mismatch_rate={report['rapidfuzz_mismatch_rate']:.4f}\n")

    diff = report["rapidfuzz_mismatch_rate"] - report["exact_mismatch_rate"]
    sign = "lower" if diff < 0 else "higher"
    print(f"Delta mismatch rate (RapidFuzz - Exact): {diff:.4f} ({sign} is better if negative)")

if __name__ == "__main__":
    main()
