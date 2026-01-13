# 🎙️ Speech to Text + Summary App

A simple web app built with **Streamlit** that lets you:

• Upload audio or video files  
• Transcribe speech into text using **Whisper (local, offline)**  
• Generate a short summary (either locally or via OpenAI)  

Supported languages:
- English (EN)
- Polish (PL)
- Ukrainian (UK)

Live demo:  
👉 https://stt-summary-app-acxmlbsdb8834doafrmer4.streamlit.app/

---

## ✨ Features

- 🎧 Upload audio or video (MP3, MP4, WAV, etc.)
- 📝 Speech-to-text transcription using `faster-whisper` (runs locally, no API needed)
- 📌 Automatic summary generation
- 🌍 Language selection: EN, PL, UK
- 🔒 OpenAI API key is **optional** and used **only for better summaries**
- ⬇️ Download transcript and summary as `.txt` files

---

## ⚙️ How it works

### Transcription
Uses `faster-whisper` locally:
- Runs on CPU
- No data leaves the server for transcription

### Summary
Two options:
1. **Local summary** (default)  
   Simple rule-based summarization, no API needed.
2. **OpenAI summary** (optional)  
   Uses GPT for higher quality summaries if you provide an API key.

---

## 🖥️ Run locally

### 1. Clone repository

```bash
git clone https://github.com/Reznikan/stt-summary-app.git
cd stt-summary-app
