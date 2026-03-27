import streamlit as st
from database import queries

def render():
    st.title("Feedback & Validation")
    st.markdown("Help improve the system by reviewing pending decisions.")
    
    # Fetch a batch of pending decisions
    df = queries.get_pending_decisions(limit=10)
    
    if df.empty:
        st.success("🎉 All caught up! No pending decisions to review.")
        return
        
    # We will just show the first one to create a "swipe" style interface
    decision = df.iloc[0]
    
    st.subheader(f"Decision #{decision['id']}")
    st.caption(f"Audio: {decision['audio_file']} | Domain: {decision['domain']}")
    
    st.markdown(f"### **{decision['action'].upper()}**: \"{decision['original_word']}\" → \"{decision['replacement_word']}\"")
    st.markdown(f"**Context:** ...{decision['context_before']}[**{decision['original_word']}**]{decision['context_after']}...")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Whisper Confidence", f"{decision['whisper_confidence']:.2f}")
    with col2:
        st.metric("Phonetic Similarity", f"{decision['phonetic_similarity']:.2f}")
    with col3:
        st.metric("LM Improvement", f"{decision['improvement']:.2f}")
    
    st.markdown("---")
    
    with st.form("feedback_form", clear_on_submit=True):
        feedback_text = st.text_area("Optional comments:")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            submit_approve = st.form_submit_button("👍 Correct (Approve)")
        with c2:
            submit_reject = st.form_submit_button("👎 Incorrect (Flag)")
        with c3:
            submit_skip = st.form_submit_button("⏭️ Skip for now")
            
        if submit_approve:
            queries.update_decision_feedback(int(decision['id']), user_approved=True, flagged=False, feedback_text=feedback_text)
            st.rerun()
        elif submit_reject:
            queries.update_decision_feedback(int(decision['id']), user_approved=False, flagged=True, feedback_text=feedback_text)
            st.rerun()
        elif submit_skip:
            # We don't have a way to easily "skip" without marking it, but we can just mark user_approved as False but flagged as False?
            # Or perhaps we should just not show it next time if we have a skip count, but for simplicity, any action here is fine.
            # But simpler: we might get stuck if we just rerun without changing anything. Let's just flag it or leave it.
            # Actually, to truly skip without an infinite loop, we might need to store skipped IDs in session_state.
            st.session_state.setdefault('skipped_ids', set()).add(int(decision['id']))
            st.rerun()
            
    # Filter out skipped IDs if any
    if 'skipped_ids' in st.session_state and st.session_state.skipped_ids:
        df = df[~df['id'].isin(st.session_state.skipped_ids)]
        if df.empty:
            st.info("You've skipped all remaining pending items in this batch. Refresh to get a new list if available.")
