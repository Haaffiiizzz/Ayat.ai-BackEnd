from fastapi import FastAPI, APIRouter, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import  Annotated
from starlette.concurrency import run_in_threadpool
from .Search import SearchVerses, SearchAudio, InitSearchCache
from .rerank import preload_reranker

app =  FastAPI(title="Muktashif")

@app.on_event("startup")
async def startup_event():
    """Preload heavy assets and caches to avoid first-request latency.

    - Preloads the cross-encoder reranker model/tokenizer.
    - Preloads embeddings (memmap), row norms, index map, and verse data.
    """
    await run_in_threadpool(preload_reranker)
    await run_in_threadpool(InitSearchCache, "app/data/embeddings.npy", "app/data/index.json", "app/data/Verses.json")
router = APIRouter()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or a list of allowed origins for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@router.get("/")
def root():
    """Health endpoint returning a simple message."""
    return {"message": "Well Hello there."}

@router.post("/uploadAudio/")
async def uploadAudio(audioFile: Annotated[UploadFile, File()]):
    """Transcribe uploaded audio, fuzzy-match against verses, and return best match."""
    audio = audioFile
    result = await run_in_threadpool(SearchAudio, audio, "null")
    if result:
        return result
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
        "VerseIndex": None,
    }
    return default
    

@router.get("/searchembedding")
async def SearchEmbed(query: str):
    """Search verses via embeddings + cross-encoder; return verse objects only."""
    results = []
    searchResult = await run_in_threadpool(SearchVerses, query)

    for result in searchResult:
        verseData = result["VerseObject"]
        results.append(verseData)

    if len(results) == 0:
        return None
    return results

    
app.include_router(router)  
