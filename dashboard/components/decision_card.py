import streamlit as st

def render(decision):
    # Use an expander for each decision
    with st.expander(f"Decision #{decision.id} – {decision.audio_file} @ {decision.timestamp}"):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{decision.action.upper()}**: \"{decision.original_word}\" → \"{decision.replacement_word}\"")
            st.write(f"Scores – Whisper: {decision.whisper_confidence:.2f}, Phonetic: {decision.phonetic_similarity:.2f}, LM improvement: {decision.improvement:.2f}")
            st.write(f"Context: …{decision.context_before}[{decision.original_word}]{decision.context_after}…")
        with col2:
            if decision.user_approved:
                st.success("👍 Approved")
            elif decision.flagged:
                st.error("⚠️ Flagged")
            else:
                st.info("⏳ Pending")
