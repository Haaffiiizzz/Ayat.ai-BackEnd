from fastapi import FastAPI, APIRouter, UploadFile, File
from typing import  Annotated
from .main2 import TranscribeAudio, LoadDataSet, ProcessMatches
from starlette.concurrency import run_in_threadpool
import json 

app =  FastAPI(title="Muktashif")
router = APIRouter( )

@router.get("/")
def root():
    return {"message": "Well Hello there."}

@router.post("/uploadAudio/")
async def uploadAudio(audioFile: Annotated[UploadFile, File()]):
    audio = audioFile.file
    
    result = await run_in_threadpool(doProcess, audio)
    if result:
        return result
    else:
        default = {"Verse": None, "Ayah": None, "Surah": None} #ayah is the text itself
        return default
    
def doProcess(audioFile):
    transcribedAudio = TranscribeAudio(audioFile)
    dataset = LoadDataSet("ArabicDataset.json")
    
    matches = ProcessMatches(transcribedAudio, dataset)
    if matches:
        
        bestMatch = matches[0]
        bestMatchDict = dataset[bestMatch[2]] #bestMatch[2] is index of the best match dict in the dtaaset list
        
        with open("FullDataset.json", "r", encoding="utf-8") as file:
            fullDataset = json.load(file)

        
        surahNumber = int(bestMatchDict["Surah"])
        verseNumber = bestMatchDict["Ayah"]

        surahDict = fullDataset[surahNumber - 1]

        nameTransliteration = surahDict["transliteration"]
        nameTranslation = surahDict["translation"]

        verseDict = surahDict["verses"][verseNumber- 1]

        verseArabic = verseDict["text"]
        verseEnglish = verseDict["translation"]

        surahInfo= f"{surahNumber}. {nameTransliteration} - {nameTranslation}"

        newDict = {"SurahInfo": surahInfo, "VerseNumber": verseNumber, "VerseArabic": verseArabic, "VerseEnglish": verseEnglish}

        
        #need to get extra info from translation json
        return bestMatchDict
    else:
        return None
    
app.include_router(router)  