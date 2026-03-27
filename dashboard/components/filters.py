import streamlit as st

def render():
    st.sidebar.subheader("Filters")
    # Date range filter (placeholder, assuming timestamp column)
    start_date = st.sidebar.date_input("Start date", value=None)
    end_date = st.sidebar.date_input("End date", value=None)
    # Audio file filter
    audio_file = st.sidebar.text_input("Audio file contains")
    # Action filter
    action = st.sidebar.selectbox("Action", ["All", "replaced", "kept_original"])
    # Domain filter
    domain = st.sidebar.text_input("Domain contains")
    # Flagged only
    flagged = st.sidebar.checkbox("Flagged only", value=False)
    # Search term
    search = st.sidebar.text_input("Search word/context")
    # Sort options
    sort_by = st.sidebar.selectbox("Sort by", ["timestamp", "whisper_confidence", "improvement", "user_approved"])
    # Assemble dict
    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "audio_file": audio_file,
        "action": action if action != "All" else None,
        "domain": domain,
        "flagged": flagged,
        "search": search,
        "sort_by": sort_by,
    }
    return {k: v for k, v in filters.items() if v not in (None, "", False)}
