import requests
import json
url = "https://cdn.jsdelivr.net/npm/quran-json@3.1.2/dist/quran_en.json"
response = requests.get(url).json()

with open("FullDataset.json", "w", encoding="utf-8") as file:
    json.dump(response, file,  indent=4, ensure_ascii=False)