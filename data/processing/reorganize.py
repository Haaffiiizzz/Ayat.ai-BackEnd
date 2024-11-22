import os
import shutil
import json

with open("data/transliterations.json", "r") as file:
    transliterationsData = json.load(file)

def reorganizeAudioFiles(audioDir, transliterationsData):
    for surahNumber, surahInfo in transliterationsData.items():
        surahName = surahInfo["name"]
        surahFolder = os.path.join(audioDir, surahName)
        if not os.path.exists(surahFolder):
            os.makedirs(surahFolder)
        for verseNumber, verseText in surahInfo["verses"].items():
            audioFilename = f"{str(surahNumber).zfill(3)}{str(verseNumber).zfill(3)}.mp3"
            audioFilePath = os.path.join(audioDir, audioFilename)
            if os.path.exists(audioFilePath):
                shutil.move(audioFilePath, os.path.join(surahFolder, audioFilename))
                print(f"Moved: {audioFilename} to {surahName} folder")
            else:
                print(f"Audio file not found: {audioFilename}")

audioDirectory = r"C:\Users\dadaa\Sudais Verse by Verse"
reorganizeAudioFiles(audioDirectory, transliterationsData)
