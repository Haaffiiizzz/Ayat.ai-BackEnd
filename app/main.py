from fastapi import FastAPI, APIRouter, UploadFile, File
from typing import  Annotated
# from .main2 import SearchKeyword
from starlette.concurrency import run_in_threadpool
import json 
from .Search import SearchVerses, SearchAudio

app =  FastAPI(title="Muktashif")
router = APIRouter( )

@router.get("/")
def root():
    return {"message": "Well Hello there."}

@router.post("/uploadAudio/")
async def uploadAudio(audioFile: Annotated[UploadFile, File()]):
    audio = audioFile.file
    
    result = await run_in_threadpool(SearchAudio, audio)
    if result:
        return result
    else:
        default = {
        "VerseID": None,
        "SurahNumber": None,
        "VerseNumber": None,
        "SurahNameArabic": None,
        "SurahNameTransliteration": None,
        "SurahNameEnglish": None,
        "VerseWithHarakat": None,
        "VerseWithoutHarakat": None,
        "VerseEnglish": None,
        "VerseIndex": None
    }

        return default
    

# @router.get("/searchkeyword")
# def Search( keyword: str):
#     result = SearchKeyword(keyword)
#     if len(result) == 0:
#         return None
#     return result

@router.get("/searchembedding")
async def SearchEmbed(query: str):
    results = []
    searchResult = await run_in_threadpool(SearchVerses, query)

    with open("app/data/VersesWithID.json", "r", encoding="utf-8") as file:
        verseIDJson = json.load(file)
    for result in searchResult:
        verseData = verseIDJson[result["verseId"]]
        verseData["VerseIndex"] = result["VerseIndex"]
        results.append(verseData)

    print(results[0])
        
    if len(results) == 0:
        return None
    return results

    
app.include_router(router)  
