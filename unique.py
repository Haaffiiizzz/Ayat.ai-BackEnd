with open("quran-dataset.txt", "r", encoding="utf-8") as file:
    dataset = file.readlines()


ayahList = []

for line in dataset:
    new = line.split("|")
    surahNo = new[0]
    ayahNo = new[1]
    ayah = new[2].strip()
    
    ayahDict = {"Surah" : surahNo, "Ayah": ayahNo, "Verse": ayah}
    ayahList.append(ayahDict)
import json
with open("dataset.json", "w", encoding="utf-8") as file:
    json.dump(ayahList, file, indent=4, ensure_ascii=False)
    
    

