# app.py
import os
import tempfile
from pathlib import Path

import streamlit as st
from faster_whisper import WhisperModel

# Optional summarization via OpenAI (requires API key)
USE_OPENAI = True
try:
    from openai import OpenAI
except Exception:
    USE_OPENAI = False

LANG_MAP = {
    "EN": "en",
    "PL": "pl",
    "UK": "uk",  # Ukrainian
}

st.set_page_config(page_title="Speech to Text + Summary", layout="wide")
st.title("Speech to Text + Summary (EN, PL, UK)")

st.sidebar.header("Settings")
lang_ui = st.sidebar.selectbox("Language", list(LANG_MAP.keys()), index=2)
model_size = st.sidebar.selectbox("Whisper model", ["tiny", "base", "small", "medium"], index=3)

summary_engine = st.sidebar.selectbox(
    "Summary engine",
    ["Local (simple)", "OpenAI (best)"],
    index=0 if not USE_OPENAI else 1
)

openai_key = ""
if summary_engine == "OpenAI (best)":
    if not USE_OPENAI:
        st.sidebar.error("OpenAI package not available. Switch to Local (simple).")
        summary_engine = "Local (simple)"
    else:
        openai_key = st.sidebar.text_input("OpenAI API key", type="password")
        st.sidebar.caption("Key is used only for summarization. Transcription is local.")

uploaded = st.file_uploader(
    "Upload audio/video",
    type=["mp3", "m4a", "mp4", "wav", "aac", "ogg", "webm", "mpeg4"],
    accept_multiple_files=False
)

@st.cache_resource
def load_model(size: str) -> WhisperModel:
    # Good defaults for CPU environments (Streamlit Cloud too)
    return WhisperModel(size, device="cpu", compute_type="int8")

def local_summary(text: str, lang_code: str) -> str:
    # very simple extractive-ish summary (no external API)
    text = text.strip()
    if not text:
        return ""
    # keep first ~5 sentences or 800 chars, whichever comes first
    import re
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out = " ".join(sentences[:5]).strip()
    if len(out) > 800:
        out = out[:800].rsplit(" ", 1)[0] + "…"
    prefix = {
        "en": "Summary:",
        "pl": "Podsumowanie:",
        "uk": "Підсумок:",
    }.get(lang_code, "Summary:")
    return f"{prefix}\n\n{out}"

def openai_summary(text: str, lang_code: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key)
    lang_name = {"en": "English", "pl": "Polish", "uk": "Ukrainian"}.get(lang_code, "English")
    prompt = (
        f"Summarize the text in {lang_name}.\n"
        "Return:\n"
        "1) 5 bullet key points\n"
        "2) 1 short paragraph summary\n"
        "Be concise.\n\n"
        f"TEXT:\n{text}"
    )
    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return resp.output_text.strip()

def save_upload_to_temp(upload) -> Path:
    suffix = Path(upload.name).suffix or ".bin"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(upload.getbuffer())
    tmp.flush()
    tmp.close()
    return Path(tmp.name)

col1, col2 = st.columns([1, 1], gap="large")

if uploaded:
    with col1:
        st.audio(uploaded)
        st.write("")

        if st.button("Transcribe", type="primary"):
            audio_path = save_upload_to_temp(uploaded)
            try:
                with st.spinner("Loading model..."):
                    model = load_model(model_size)

                with st.spinner("Transcribing..."):
                    segments, info = model.transcribe(
                        str(audio_path),
                        language=LANG_MAP[lang_ui],
                        vad_filter=True
                    )
                    transcript = "".join(seg.text for seg in segments).strip()

                st.session_state["transcript"] = transcript

                # Auto-summary after transcription
                if transcript:
                    with st.spinner("Summarizing..."):
                        if summary_engine == "OpenAI (best)":
                            if not openai_key:
                                st.warning("Enter an OpenAI API key to use OpenAI summarization.")
                                summary = local_summary(transcript, LANG_MAP[lang_ui])
                            else:
                                summary = openai_summary(transcript, LANG_MAP[lang_ui], openai_key)
                        else:
                            summary = local_summary(transcript, LANG_MAP[lang_ui])

                    st.session_state["summary"] = summary
                else:
                    st.session_state["summary"] = ""

            finally:
                # clean up temp file
                try:
                    os.unlink(str(audio_path))
                except Exception:
                    pass

with col2:
    st.subheader("Transcript")
    transcript_val = st.session_state.get("transcript", "")
    st.text_area("",
                 value=transcript_val,
                 height=260,
                 key="transcript_box")

    if transcript_val:
        st.download_button(
            "Download transcript (.txt)",
            data=transcript_val,
            file_name="transcript.txt",
            mime="text/plain"
        )

    st.subheader("Summary")
    summary_val = st.session_state.get("summary", "")
    st.text_area("",
                 value=summary_val,
                 height=220,
                 key="summary_box")

    if summary_val:
        st.download_button(
            "Download summary (.txt)",
            data=summary_val,
            file_name="summary.txt",
            mime="text/plain"
        )

st.caption(
    "Notes: Transcription runs locally using faster-whisper. "
    "OpenAI key is only needed if you choose OpenAI summarization."
)
