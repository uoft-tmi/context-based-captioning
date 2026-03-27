import streamlit as st
import tempfile
import os
import sys
from keyword_extractor import KeywordExtractor

def render():
    st.header("🔑 Hotword Extraction")
    st.write("Upload your lecture notes (PDF or TXT) to extract domain-specific keywords for the rescorer.")

    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'txt'])

    if uploaded_file is not None:
        with st.status("Extracting hotwords...", expanded=True) as status:
            # Save uploaded file to a temporary file
            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                extractor = KeywordExtractor()
                keywords = extractor.extract_from_file(tmp_path)
                status.update(label="Extraction complete!", state="complete")
            except Exception as e:
                st.error(f"Error extracting keywords: {e}")
                keywords = []
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            
        if keywords:
            st.success(f"Found {len(keywords)} terms in your notes.")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("### Copy-Paste for `hotwords.txt`")
                st.text_area("Keywords", value="\n".join(keywords), height=300)
            
            with col2:
                st.write("### List View")
                for kw in keywords:
                    st.markdown(f"- {kw}")
