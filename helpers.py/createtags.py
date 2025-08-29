import re
import nltk
import spacy
from nltk.corpus import stopwords
import json

# Download stopwords
nltk.download("stopwords")


stopWords = list(set(stopwords.words("english")))
with open("stopwords.json", "w", encoding="utf-8") as file:
    json.dump(stopWords, file, indent=2)


nlp = spacy.load("en_core_web_sm")

def extractTags(text: str):
    
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)  # remove punctuation/numbers
    
    doc = nlp(text)
    tags = []
    for token in doc:
        if token.text not in stopWords and token.is_alpha:
            tags.append(token.lemma_)  # lemmatized
    return list(set(tags))

tagsList = []
with open("app/data/Verses.json", "r", encoding="utf-8") as file:
    verseList = json.load(file)
    i = 1
    for verse in verseList:
        print(i)
        i+= 1
        tagsList.append({"VerseID": verse["VerseID"], "tags": extractTags(verse["VerseEnglish"])})

with open("app/data/Tags.json", "w", encoding="utf-8") as file:
    json.dump(tagsList, file, indent=4)
