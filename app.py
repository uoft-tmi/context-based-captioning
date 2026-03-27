import streamlit as st
import os
import tempfile
import torch
from asr_engine import ASREngine
from lm_rescorer import LMRescorer
from phonetic_matcher import PhoneticMatcher
from fusion_processor import FusionProcessor
from keyword_extractor import KeywordExtractor

# --- Page Config ---
st.set_page_config(page_title="Lecture Shallow Fusion", page_icon="🎓", layout="wide")

st.title("🎓 Lecture Shallow Fusion")
st.markdown("""
Upload your **lecture notes** (PDF/TXT) and **lecture audio** to get a rescored transcript. 
This system uses BERT to extract key phrases and Shallow Fusion to correct the ASR output.
""")

# --- Sidebar Configuration ---
st.sidebar.header("Configuration")
whisper_model_name = st.sidebar.selectbox("Whisper Model", ["tiny", "base", "small"], index=0)
llm_model_name = st.sidebar.selectbox("LM Model", ["gpt2", "distilgpt2"], index=0)
conf_threshold = st.sidebar.slider("ASR Confidence Threshold", 0.0, 1.0, 0.7)
phonetic_threshold = st.sidebar.slider("Phonetic Similarity Threshold", 0.0, 1.0, 0.35)
lambda_lm = st.sidebar.slider("LM Weight (Lambda)", 0.0, 2.0, 1.0)

# --- Resource Caching ---
@st.cache_resource
def load_models(whisper_name, llm_name):
    asr = ASREngine(model_name=whisper_name)
    lm = LMRescorer(model_name=llm_name)
    kw_extractor = KeywordExtractor(model_name="all-MiniLM-L6-v2") # Optimized BERT
    return asr, lm, kw_extractor

# --- Main Logic ---
col1, col2 = st.columns(2)

with col1:
    st.header("1. Upload Lecture Notes")
    notes_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])

with col2:
    st.header("2. Upload Lecture Audio")
    audio_file = st.file_uploader("Upload MP3, WAV, or M4A", type=["mp3", "wav", "m4a"])

if notes_file and audio_file:
    if st.button("Process Lecture"):
        with st.status("Processing...", expanded=True) as status:
            # 1. Load Models
            status.update(label="Loading AI Models...")
            asr, lm, kw_extractor = load_models(whisper_model_name, llm_model_name)

            # 2. Extract Keywords
            status.update(label="Extracting Hotwords from Notes...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(notes_file.name)[1]) as tmp_notes:
                tmp_notes.write(notes_file.getvalue())
                notes_path = tmp_notes.name
            
            hotwords = kw_extractor.extract_from_file(notes_path)
            st.write(f"**Extracted {len(hotwords)} hotwords:**")
            st.write(", ".join(hotwords))
            os.unlink(notes_path)

            # 3. Transcribe Audio
            status.update(label="Transcribing Audio (Whisper)...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp_audio:
                tmp_audio.write(audio_file.getvalue())
                audio_path = tmp_audio.name
            
            # Note: asr.transcribe currently takes numpy array, but whisper.transcribe takes path too.
            # Let's use the path directly for standard whisper results in this UI context.
            # I'll update ASREngine slightly or handle it here.
            # Actually, I'll update ASREngine.transcribe to handle paths.
            
            import whisper
            # Using raw whisper here for simplicity in file-based UI
            result = asr.model.transcribe(audio_path, word_timestamps=True, language="en")
            words = []
            for segment in result.get("segments", []):
                for word_info in segment.get("words", []):
                    words.append({
                        "word": word_info["word"].strip(),
                        "start": word_info["start"],
                        "end": word_info["end"],
                        "probability": word_info.get("probability", 1.0)
                    })
            os.unlink(audio_path)

            # 4. Shallow Fusion Rescoring
            status.update(label="Rescoring with Shallow Fusion...")
            matcher = PhoneticMatcher(hotwords)
            processor = FusionProcessor(
                asr_engine=asr,
                phonetic_matcher=matcher,
                lm_rescorer=lm,
                confidence_threshold=conf_threshold,
                phonetic_threshold=phonetic_threshold,
                lambda_lm=lambda_lm
            )
            
            rescored_text, logs = processor.process_words(words)
            status.update(label="Complete!", state="complete")

        # --- Display Results ---
        st.divider()
        st.subheader("Rescored Transcript")
        st.write(rescored_text)

        if logs:
            st.subheader("Corrections Made")
            for log in logs:
                st.info(f"Fixed: **{log['original']}** → **{log['replacement']}** (Confidence: {log['confidence']:.2f})")
else:
    st.info("Please upload both notes and audio to begin.")
