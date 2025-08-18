import whisper
import os
import json
from rapidfuzz import process, fuzz
import time
import tempfile


#load model
model = whisper.load_model("small")

def TranscribeAudio(audioFile) -> str:
    '''
    Use Whisper Model to transcribe the audio file given as a file-like object, 
    and return the transcribed audio.
    '''

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(audioFile.read())
        tmp_path = tmp.name

    TranscribedObject: dict = model.transcribe(tmp_path, language="ar")
    AyahText = TranscribedObject["text"].strip()

    os.remove(tmp_path)

    return AyahText


def LoadDataSet(DatasetPath: str) -> list:
    
    with open(DatasetPath, "r", encoding="utf-8") as file:
        dataset: list = json.load(file)
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

def ProcessMatches(ResultAyah: str, Dataset: list):
    
    #this returns a list of tuples where each tuple is (Verse, similarity percentage, index of verse in dataset)

    matches = process.extract(
        ResultAyah,
        [i["Verse"] for i in Dataset],
        scorer=fuzz.token_set_ratio,
        score_cutoff=70,
        limit=None
    ) 
    
    matches.sort(key= lambda x: x[1], reverse=True )
    return matches

def SearchKeyword(Keyword: str) -> list:
    with open("FullDataset.json", "r", encoding="utf-8") as datasetFile:
        dataset: list = json.load(datasetFile)

    result = []

    for surah in dataset:
        verses = surah["verses"]
        for verse in verses:
            if Keyword in verse["translation"]:
                verseData = {"SurahNumber": surah["id"], "VerseNumber": verse["id"], "VerseArabic": verse["text"], "VerseEnglish": verse["translation"]}
                result.append(verseData)
                
    return result


# def main():
#     ayahPath = "Test2.mp3"
#     transcribedAudio = TranscribeAudio(ayahPath)
    
#     dataset = LoadDataSet("dataset.json")
    
#     matches = ProcessMatches(transcribedAudio, dataset)
#     if matches:
        
#         bestMatch = matches[0]
#         bestMatchDict = dataset[bestMatch[2]] #bestMatch[2] is the index of bestmatch in  dataset
        
#         print(f"Surah Number: {bestMatchDict['Surah']}\nVerse Number: {bestMatchDict['Ayah']}\nVerse: {bestMatchDict['Verse']}")
#     else:
#         print("Close match not found!")
    

# if __name__ == "__main__":
#     main()