with open("Verses.json", "r", encoding="utf-8") as file:
    import json
    fileJson = json.load(file)
    for i in range(len(fileJson)):
        fileJson[i]["VerseIndex"] = i + 1
    
    with open("newVerse.json", "w", encoding="utf-8") as newFile:
        json.dump(fileJson, newFile, indent=4, ensure_ascii=False)