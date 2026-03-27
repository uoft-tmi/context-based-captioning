import streamlit as st
import os
import sys

# Ensure project root is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Set page configuration
st.set_page_config(page_title="Rescoring Dashboard", layout="wide")

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigate",
    ["Hotword Extraction", "Decision Log", "Analytics", "Feedback", "Safety Metrics", "Export & Reporting"]
)

# Dynamically import and render the selected page
if page == "Hotword Extraction":
    from pages import hotword_extraction
    hotword_extraction.render()
elif page == "Decision Log":
    from pages import decision_log
    decision_log.render()
elif page == "Analytics":
    from pages import analytics
    analytics.render()
elif page == "Feedback":
    from pages import feedback
    feedback.render()
elif page == "Safety Metrics":
    from pages import safety_metrics
    safety_metrics.render()
elif page == "Export & Reporting":
    from pages import export
    export.render()
