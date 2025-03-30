
from google.cloud import speech_v1p1beta1 as speech
import io

# Initialize client
client = speech.SpeechClient()

# Load audio file
with io.open(r"C:\Users\dadaa\Sudais Verse by Verse\001_Al-Fatiha - The Opening\001001.mp3", "rb") as audio_file:
    content = audio_file.read()

# Configure request
audio = {"content": content}
config = {
    "language_code": "ar-SA",  # Arabic Saudi for better Quranic pronunciation support
    "enable_word_time_offsets": True,
}

response = client.recognize(config=config, audio=audio)

# Print results
for result in response.results:
    print(f"Transcript: {result.alternatives[0].transcript}")
