import whisper
import os
import json
from rapidfuzz import process, fuzz

os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

model = whisper.load_model("small")

result = model.transcribe("Test2.mp3", language="ar")
resultAyah = result["text"].strip()
print("Transcribed audio", resultAyah)

with open("dataset.json", "r", encoding="utf-8") as file:
    dataset = json.load(file)

windowSize = 2
chunks = []
for i in range(len(dataset) - windowSize + 1):
    chunkText = " ".join([dataset[i + j]["Verse"] for j in range(windowSize)])
    chunks.append({
        "text": chunkText,
        "startIndex": i,
        "verses": [dataset[i + j] for j in range(windowSize)]
    })

matches = process.extract(
    resultAyah,
    [c["text"] for c in chunks],
    scorer=fuzz.token_set_ratio,
    score_cutoff=70,
    limit=None
) #this returns a list of tuples where each tuple is (chunked ayats, similarity percentage, index of chunk in chunks list)

print(matches)

rankedMatches = []

for matchText, score, idx in matches:
    chunk = chunks[idx]
    firstVerseText = chunk["verses"][0]["Verse"]
    secondVerseText = chunk["verses"][1]["Verse"]

    scoreFirst = fuzz.token_set_ratio(resultAyah, firstVerseText)
    scoreSecond = fuzz.token_set_ratio(resultAyah, secondVerseText)

    isFirstVerseBest = scoreFirst >= scoreSecond

    rankedMatches.append({
        "chunk": chunk,
        "overallScore": score,
        "isFirstVerseBest": isFirstVerseBest
    })

rankedMatches.sort(
    key=lambda x: (x["isFirstVerseBest"], x["overallScore"]),
    reverse=True
)

if rankedMatches:
    best = rankedMatches[0]
    print("Best matching chunk ({} verses):".format(windowSize))
    for verse in best["chunk"]["verses"]:
        print(verse)
    print("\nSimilarity score:", best["overallScore"])
    print("Matched first verse:", best["isFirstVerseBest"])
else:
    print("No matching chunk found above threshold.")
def main():
    print()

if __name__ == "__main__":
    main()