import whisper
import os
import json
from rapidfuzz import fuzz


os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"
model = whisper.load_model("small")
result = model.transcribe("Maryam8.mp3", language="ar")
resultAyah = result["text"].strip()

with open("dataset.json", "r", encoding="utf-8") as file:
    dataset = json.load(file)
possibleResults = []

for verse in dataset:
    similarity = int(fuzz.ratio(resultAyah, verse["Verse"]))
    if similarity >= 80:
        possibleResults.append({"Verse": verse, "Similarity": similarity})
print("Possible Results:\n", possibleResults)
print()
bestResult = max(possibleResults, key= lambda x: x["Similarity"])

print(bestResult)