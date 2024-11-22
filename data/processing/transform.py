import json

with open("data/data.json", "r") as file:
    data = json.load(file)

newData = {}

for surahKey, verses in data.items():
    surahNumber, surahName = surahKey.split(". ", 1)
    surahNumber = int(surahNumber.strip())

    newData[surahNumber] = {
        "name": surahName,
        "verses": {}
    }

    for verseNumber, verseText in verses.items():
        newData[surahNumber]["verses"][verseNumber] = verseText

with open("data/transliterations.json", "w") as file:
    json.dump(newData, file, indent=4)

