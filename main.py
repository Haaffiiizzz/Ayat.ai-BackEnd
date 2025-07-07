import whisper
import os
import json
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"
model = whisper.load_model("small")
result = model.transcribe("001001.mp3", language="ar")
with open("test.json", "w", encoding="utf-8") as file:
    json.dump(result, file)

