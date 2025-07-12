import whisper
import os
import json
from rapidfuzz import process, fuzz

os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"
model = whisper.load_model("small")
result = model.transcribe("Maryam8.mp3", language="ar")
resultAyah = result["text"].strip()

with open("dataset.json", "r", encoding="utf-8") as file:
    dataset = json.load(file)


verses = [verse["Verse"] for verse in dataset]

best_match = process.extractOne(
    resultAyah,
    verses,
    scorer=fuzz.token_sort_ratio,
    score_cutoff=80
)

if best_match:
    match_text, score, idx = best_match
    best_result = dataset[idx]
    print("Best result:\n", best_result, "\nSimilarity:", score)
else:
    print("No matching results found above threshold.")