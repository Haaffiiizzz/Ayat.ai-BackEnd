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

windowSize = 2
chunks = []
for i in range(len(dataset) - windowSize + 1):
    chunkText = " ".join([dataset[i + j]["Verse"] for j in range(windowSize)])
    chunks.append({
        "text": chunkText,
        "start_index": i,
        "verses": [dataset[i + j] for j in range(windowSize)]
    })

print(chunks, len(chunks))

best_match = process.extractOne(
    resultAyah,
    [c["text"] for c in chunks],
    scorer=fuzz.token_set_ratio,
    score_cutoff=70
)

if best_match:
    match_text, score, idx = best_match
    best_chunk = chunks[idx]
    print("Best matching chunk ({} verses):".format(windowSize))
    for verse in best_chunk["verses"]:
        print(verse)
    print("\nSimilarity score:", score)
else:
    print("No matching chunk found above threshold.")
