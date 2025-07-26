import whisper
import os
import json
from rapidfuzz import process, fuzz

os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

def TranscribeAudio(AudioPath: str) -> str:
    '''
    Use Whisper Model to trancribe the audio file given its path, and return the transcribed audio
    '''
    
    #load model
    
    model = whisper.load_model("small")
    
    TranscribedObject: dict = model.transcribe(AudioPath, language="ar")
    AyahText = TranscribedObject["text"].strip()
    return AyahText

def LoadDataSet(DatasetPath: str) -> dict:
    
    with open(DatasetPath, "r", encoding="utf-8") as file:
        dataset: dict = json.load(file)
    return dataset

def CreateChunks(Dataset: dict, WindowSize: int) -> list:
    #Return a list of joined verses in chunks of 2, 3.. depending on WindowSize.
    chunks = []
    for i in range(len(Dataset) - WindowSize + 1):
        chunkText = " ".join([Dataset[i + j]["Verse"] for j in range(WindowSize)])
        chunks.append({
            "text": chunkText,
            "startIndex": i,
            "verses": [Dataset[i + j] for j in range(WindowSize)]
        })
    return chunks

def ProcessMatches(ResultAyah: str, chunks: list):
    
    #this returns a list of tuples where each tuple is (chunked ayats, similarity percentage, index of chunk in chunks list)

    matches = process.extract(
        ResultAyah,
        [c["text"] for c in chunks],
        scorer=fuzz.token_set_ratio,
        score_cutoff=70,
        limit=None
    ) 
    return matches

def 
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