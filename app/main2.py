import os
import json
from rapidfuzz import process, fuzz
import tempfile
import numpy as np
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

def l2_normalize(mat: np.ndarray, axis=1, eps=1e-12):
    norm = np.sqrt((mat * mat).sum(axis=axis, keepdims=True)).clip(min=eps)
    return mat / norm
# Model will be loaded in main.py startup event

# EmbeddingModel = SentenceTransformer("all-MiniLM-L6-v2")
# embeddings = np.load("app/data/verses_emb_minilm_cosine.npy")
# embeddings = l2_normalize(np.asarray(embeddings))
# df = pd.read_json("app/data/Verses.json")
# df["VerseEnglish"] = df["VerseEnglish"].fillna("").str.strip()


client = OpenAI()

import re

def removeHarakat(text: str) -> str:
    harakatPattern = re.compile(r'[\u0617-\u061A\u064B-\u0652]')
    return harakatPattern.sub('', text)

def TranscribeAudio(audioFile, model) -> str:
    '''
    Use Whisper API to transcribe the audio file given as a file-like object, 
    and return the transcribed audio.
    '''
    # TranscribedObject: dict = model.transcribe(tmp_path, language="ar")
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audioFile.filename.split('.')[-1]}") as tmp:
        tmp.write(audioFile.file.read())
        tmp_path = tmp.name


    with open(tmp_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="ar"
        )

    ayahText = transcription.text.strip()
    ayahText = removeHarakat(ayahText)

    os.remove(tmp_path)

    return ayahText


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
        [i["VerseWithoutHarakat"] for i in Dataset],
        scorer=fuzz.token_set_ratio,
        score_cutoff=65,
        limit=None
    ) 
    
    matches.sort(key= lambda x: x[1], reverse=True )
    return matches

# def SearchKeyword(Keyword: str) -> list:
#     with open("FullDataset.json", "r", encoding="utf-8") as datasetFile:
#         dataset: list = json.load(datasetFile)

#     result = []

#     for surah in dataset:
#         verses = surah["verses"]
#         for verse in verses:
#             if Keyword.strip().lower() in verse["translation"].strip().lower():
#                 surahInfo = f"{surah['id']}. {surah['transliteration']} - {surah['translation']}"
#                 verseData = {"SurahInfo": surahInfo, "VerseNumber": verse["id"], "VerseArabic": verse["text"], "VerseEnglish": verse["translation"]}
#                 result.append(verseData)
                
#     return result

# def SearchEmbedding(Query: str, limit: int = 25 ) -> list:
    
#     q = EmbeddingModel.encode_query(Query, normalize_embeddings=True)
#     scores = embeddings @ q  # cosine similarity
#     topk = np.argpartition(-scores, kth=min(limit, len(scores)-1))[:limit]
#     topk = topk[np.argsort(-scores[topk])]
#     results = df.iloc[topk][[
#         "SurahNumber", "VerseNumber", "VerseWithHarakat", "VerseEnglish"
#     ]].copy()
#     results["score"] = scores[topk]
    
#     return results.to_dict(orient="records")



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