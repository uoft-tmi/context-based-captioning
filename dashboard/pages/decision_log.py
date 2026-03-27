import streamlit as st
from database import queries
from components import filters, decision_card

def render():
    st.title("Decision Log")
    # Render filter UI
    filter_params = filters.render()
    # Fetch decisions
    df = queries.get_decisions(**filter_params)
    # Pagination
    page = st.experimental_get_query_params().get("page", [0])[0]
    page = int(page)
    page_size = 20
    start = page * page_size
    end = start + page_size
    for _, row in df.iloc[start:end].iterrows():
        decision_card.render(row)
    # Export button
    if st.button("Export CSV"):
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, "decisions.csv", "text/csv")
