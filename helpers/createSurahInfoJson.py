import json
with open("FullDataset.json", "r", encoding="utf-8") as file:
    fullDataset = json.load(file)
    surahInfoDict = {}
    for surah in fullDataset:
        number = surah["id"]

        surahDict = {}
        nameArabic = surah["name"]
        nameTransliteration = surah["transliteration"]
        nameEnglish = surah["translation"]
        surahInfo = f"{number}. {nameTransliteration} - {nameEnglish}"

        surahDict["SurahNameArabic"] = nameArabic
        surahDict["SurahNameTransliteration"] = nameTransliteration
        surahDict["SurahNameEnglish"] = nameEnglish
        surahDict["SurahInfo"] = surahInfo

        surahInfoDict[number] = surahDict
        
    with open("SurahInfo.json", "w", encoding="utf-8") as surahJson:
        json.dump(surahInfoDict, surahJson, indent=4, ensure_ascii=False)