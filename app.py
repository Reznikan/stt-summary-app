import os
import tempfile
from pathlib import Path

import streamlit as st
import whisper

# Optional OpenAI summarization
USE_OPENAI = True
try:
    from openai import OpenAI
except Exception:
    USE_OPENAI = False


LANG_MAP = {
    "EN": "en",
    "PL": "pl",
    "UK": "uk",
}

st.set_page_config(page_title="Speech to Text + Summary", layout="wide")
st.title("Speech to Text + Summary (EN, PL, UK)")

st.sidebar.header("Settings")
lang_ui = st.sidebar.selectbox("Language", ["EN", "PL", "UK"])
model_size = st.sidebar.selectbox("Whisper model", ["tiny", "base", "small", "medium"], index=2)

summarizer_choice = st.sidebar.selectbox(
    "Summary engine",
    ["Local (basic)", "OpenAI (best)"],
    index=0 if not USE_OPENAI else 1
)

openai_api_key = None
if summarizer_choice == "OpenAI (best)":
    if not USE_OPENAI:
        st.sidebar.error("OpenAI library not installed. Run: python -m pip install openai")
    openai_api_key = st.sidebar.text_input("OpenAI API key", type="password")
    st.sidebar.caption("Key is used only for summarization. Transcription is local.")

uploaded = st.file_uploader("Upload audio/video", type=["mp3", "m4a", "mp4", "wav", "aac", "ogg", "webm"])

def basic_summary(text: str, max_bullets: int = 7) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return "No content to summarize."
    lines_sorted = sorted(lines, key=len, reverse=True)
    picked = []
    for ln in lines_sorted:
        if len(picked) >= max_bullets:
            break
        if ln not in picked and len(ln) > 40:
            picked.append(ln)
    if not picked:
        picked = lines[:max_bullets]
    return "\n".join([f"- {p}" for p in picked])

def openai_summary(text: str, lang: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key)
    prompt = f"""
Summarize the following transcript in {lang}.
Return:
1) 5-8 bullet key points
2) Action items (if any)
3) 1 sentence TL;DR

Transcript:
{text}
""".strip()

    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )
    return resp.output_text.strip()

if uploaded:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / uploaded.name
        tmp_path.write_bytes(uploaded.getvalue())

        st.audio(uploaded)

        if st.button("Transcribe"):
            with st.spinner("Loading Whisper model..."):
                model = whisper.load_model(model_size)

            with st.spinner("Transcribing..."):
                result = model.transcribe(
                    str(tmp_path),
                    language=LANG_MAP[lang_ui],
                    fp16=False
                )
                transcript = result.get("text", "").strip()

            st.subheader("Transcript")
            st.text_area("", transcript, height=250)

            st.download_button(
                "Download transcript (.txt)",
                data=transcript.encode("utf-8"),
                file_name=f"{tmp_path.stem}_{LANG_MAP[lang_ui]}.txt",
                mime="text/plain"
            )

            st.subheader("Summary")
            if summarizer_choice == "OpenAI (best)":
                if not openai_api_key:
                    st.warning("Enter your OpenAI API key in the sidebar to generate summary.")
                else:
                    with st.spinner("Summarizing with OpenAI..."):
                        summary = openai_summary(transcript, lang_ui, openai_api_key)
                    st.text_area("", summary, height=250)
                    st.download_button(
                        "Download summary (.txt)",
                        data=summary.encode("utf-8"),
                        file_name=f"{tmp_path.stem}_{LANG_MAP[lang_ui]}_summary.txt",
                        mime="text/plain"
                    )
            else:
                summary = basic_summary(transcript)
                st.text_area("", summary, height=250)
                st.download_button(
                    "Download summary (.txt)",
                    data=summary.encode("utf-8"),
                    file_name=f"{tmp_path.stem}_{LANG_MAP[lang_ui]}_summary.txt",
                    mime="text/plain"
                )

else:
    st.info("Upload a file to start.")
