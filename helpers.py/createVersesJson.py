import json

# load both files
with open("FullDataset.json", "r", encoding="utf-8") as f:
    fullDataset = json.load(f)

with open("ArabicDataset.json", "r", encoding="utf-8") as f:
    arabicDataset = json.load(f)

# make lookup for arabic no-harakat
arabicLookup = {(int(v["Surah"]), int(v["Ayah"])): v["Verse"] for v in arabicDataset}

versesList = []

for surah in fullDataset:
    surahId = int(surah["id"])
    for verse in surah["verses"]:
        ayahId = int(verse["id"])
        versesList.append({
            "VerseID": f"{surahId}:{ayahId}",             # add back id
            "SurahNumber": surahId,
            "VerseNumber": ayahId,
            "SurahNameArabic": surah["name"],
            "SurahNameTransliteration": surah["transliteration"],
            "SurahNameEnglish": surah["translation"],
            "VerseWithHarakat": verse["text"],                          # with harakat
            "VerseWithoutHarakat": arabicLookup.get((surahId, ayahId), ""),  # from ArabicDataset
            "VerseEnglish": verse["translation"]
        })

# save merged list
with open("Verses.json", "w", encoding="utf-8") as f:
    json.dump(versesList, f, ensure_ascii=False, indent=4)

print(f"Saved {len(versesList)} verses")
