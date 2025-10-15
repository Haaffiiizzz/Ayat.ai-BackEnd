import os
import json
import tempfile
import re
from rapidfuzz import process, fuzz
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


def removeHarakat(text: str) -> str:
    """Remove Arabic diacritics (harakat) from text."""
    harakatPattern = re.compile(r"[\u0617-\u061A\u064B-\u0652]")
    return harakatPattern.sub("", text)


def TranscribeAudio(audioFile, model) -> str:
    """Transcribe an uploaded audio file with Whisper and return cleaned text."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audioFile.filename.split('.')[-1]}") as tmp:
        tmp.write(audioFile.file.read())
        tmpPath = tmp.name

    with open(tmpPath, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="ar",
        )

    ayahText = removeHarakat(transcription.text.strip())
    os.remove(tmpPath)
    return ayahText


def LoadDataSet(datasetPath: str) -> list:
    """Load verse dataset JSON into a list of dicts."""
    with open(datasetPath, "r", encoding="utf-8") as file:
        dataset: list = json.load(file)
    return dataset


def ProcessMatches(resultAyah: str, dataset: list):
    """Return fuzzy matches as tuples: (text, score, index) sorted by score desc."""
    matches = process.extract(
        resultAyah,
        [i["VerseWithoutHarakat"] for i in dataset],
        scorer=fuzz.token_set_ratio,
        score_cutoff=65,
        limit=None,
    )
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches
