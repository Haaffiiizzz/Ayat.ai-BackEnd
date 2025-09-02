# Ayat.ai 🎙️📖
**AI-powered Quran recitation recognition and semantic search**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![React Native](https://img.shields.io/badge/React%20Native-0.7x-blue.svg)](https://reactnative.dev/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Embeddings%20v3%20Large-ff6f00.svg)](https://platform.openai.com/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## 📌 Overview
**Ayat.ai** is a first-of-its-kind AI platform that can:
- 🎧 Recognize **Quranic verses** from **audio recitations**  
- 🔎 Support **keyword search** and **semantic retrieval** across all **114 surahs / 6,236 verses**  
- 🏷️ Leverage **tag-based metadata** for contextual verse exploration  
- 📱 Provide a **React Native frontend** for a smooth, cross-platform user experience  

---

## ⚡ Features
- **Automatic Speech Recognition (ASR)** using [OpenAI Whisper] for transcribing Romanized Arabic recitations  
- **Semantic search** with [OpenAI Embeddings v3 Large] + cosine similarity  
- **Tagging system** for enhanced filtering and verse categorization  
- **Partial recitation handling** using RapidFuzz similarity search  
- **FastAPI backend** for scalable API endpoints  
- **React Native frontend** for mobile-friendly verse lookup and exploration  
- Benchmarked on **974 Arabic partial-recitation queries** → RapidFuzz expanded coverage by **~49%** with **87% accuracy@1**  

---

## 🛠️ Tech Stack
- **Backend:** FastAPI, Python  
- **Frontend:** React Native, Expo  
- **AI/ML:** OpenAI Whisper, OpenAI Embeddings v3 Large, RapidFuzz  
- **Database:** (currently JSON storage; extendable to Supabase / vector DB)  
- **Deployment:** Docker (planned), Heroku/Supabase (roadmap)  

---
