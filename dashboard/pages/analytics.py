import streamlit as st
from database import queries
from components import charts

def render():
    st.title("Analytics")
    # Fetch all decisions (could add filters later)
    df = queries.get_decisions()
    if df.empty:
        st.info("No decisions available to display analytics.")
        return
    # Overview metrics
    charts.overview_chart(df)
    st.markdown("---")
    # Time series
    charts.replacement_rate_time_series(df)
    st.markdown("---")
    # Domain breakdown
    charts.domain_breakdown_chart(df)
    st.markdown("---")
    # Confidence histogram
    charts.confidence_histogram(df)
    st.markdown("---")
    # Top replacements
    charts.top_replacements(df)
