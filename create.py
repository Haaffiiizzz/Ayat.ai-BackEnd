import json
with open("quran-dataset.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()
    res = []
    for line in lines:
        
        new = {}
        line = line.split("|")
        surah = line[0]
        ayahNo = line[1]
        verse = line[2]
        new["Surah"] = surah
        new["Ayah"] = ayahNo
        new["Verse"] = verse.strip()

        res.append(new)
    with open("dataset.json", "w", encoding="utf-8") as newFile:
        json.dump(res, newFile,indent=4, ensure_ascii=False)
