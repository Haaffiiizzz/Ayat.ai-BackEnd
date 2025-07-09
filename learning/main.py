import whisper

model = whisper.load_model("small")
result = model.transcribe("your_audio.mp3", language="ar")
print(result["text"])
