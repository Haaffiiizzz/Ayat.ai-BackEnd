from fastapi import FastAPI, APIRouter, UploadFile, File

from fastapi.middleware.cors import CORSMiddleware
from typing import  Annotated
# from .main2 import SearchKeyword
from starlette.concurrency import run_in_threadpool
import json 
from .Search import SearchVerses, SearchAudio
import whisper

app =  FastAPI(title="Muktashif")

@app.on_event("startup")
async def startup_event():
    """Load the Whisper model on startup and store it in app state"""
    print("Loading Whisper model...")
    app.state.whisper_model = whisper.load_model("small")
    print("Whisper model loaded successfully!")
router = APIRouter( )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or a list of allowed origins for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@router.get("/")
def root():
    return {"message": "Well Hello there."}

@router.post("/uploadAudio/")
async def uploadAudio(audioFile: Annotated[UploadFile, File()]):
    audio = audioFile.file
    
    result = await run_in_threadpool(SearchAudio, audio, app.state.whisper_model)
    print("result ", result)
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

    
    for result in searchResult:
        verseData = result["VerseObject"]
        results.append(verseData)

        
    if len(results) == 0:
        return None
    # print(results[:15])
    return results

    
app.include_router(router)  
