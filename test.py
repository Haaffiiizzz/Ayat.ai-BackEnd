import requests

url = "http://localhost:8000/uploadAudio"
files = {'audioFile': open("Test1.mp3", 'rb')}

response = requests.post(url, files=files)
print(response.json())