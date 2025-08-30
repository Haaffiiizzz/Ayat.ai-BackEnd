import json

def restructureVerses(inputPath="app/data/Verses.json", outputPath="app/data/VersesWithID.json"):
    # load array of verse dicts
    with open(inputPath, "r", encoding="utf-8") as f:
        versesList = json.load(f)

    # restructure into dict with VerseID as key
    versesDict = {v["VerseID"]: v for v in versesList}

    # save new dict
    with open(outputPath, "w", encoding="utf-8") as f:
        json.dump(versesDict, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(versesDict)} verses to {outputPath}")

if __name__ == "__main__":
    restructureVerses()
