[# Speech to Text + Summary App

A simple Streamlit app for:
- Speech-to-text transcription using Whisper (local)
- Text summarization using OpenAI (optional)

## Supported languages
- English (EN)
- Polish (PL)
- Ukrainian (UK)

## Features
- Upload audio or video files (MP3, MP4, WAV, M4A)
- Local transcription (no API key needed)
- Optional AI summary (requires OpenAI API key)
- Simple web interface

## How it works
- Transcription runs locally using Whisper
- Summarization is done via OpenAI API (if enabled)

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
](https://stt-summary-app-acxmlbsdb8834doafrmer4.streamlit.app/)
