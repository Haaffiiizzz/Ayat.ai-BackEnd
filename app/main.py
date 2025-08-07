from fastapi import FastAPI, APIRouter, UploadFile, File
from typing import  Annotated
from .main2 import TranscribeAudio, LoadDataSet, ProcessMatches
from starlette.concurrency import run_in_threadpool

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
    dataset = LoadDataSet("dataset.json")
    
    matches = ProcessMatches(transcribedAudio, dataset)
    if matches:
        
        bestMatch = matches[0]
        bestMatchDict = dataset[bestMatch[2]] #bestMatch[2] is the index of bestmatch in  dataset
        
        return bestMatchDict
    else:
        return None
    
app.include_router(router)  