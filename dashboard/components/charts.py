import streamlit as st
import plotly.express as px
import pandas as pd

# Example chart functions – these will be called from the analytics page

def overview_chart(df: pd.DataFrame):
    """Render big-number overview metrics as columns."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Words", int(df['total_words'].sum()))
    with col2:
        st.metric("Words Rescored", int(df['words_rescored'].sum()))
    with col3:
        replacement_rate = df['words_rescored'].sum() / df['total_words'].sum() * 100 if df['total_words'].sum() else 0
        st.metric("Replacement Rate", f"{replacement_rate:.1f}%")
    with col4:
        approval_rate = df['user_approved'].mean() * 100 if 'user_approved' in df.columns else 0
        st.metric("User Approval", f"{approval_rate:.1f}%")

def replacement_rate_time_series(df: pd.DataFrame):
    """Line chart of replacement rate over time (by day)."""
    df = df.copy()
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily = df.groupby('date').apply(lambda x: (x['action'] == 'replaced').mean())
    daily = daily.reset_index(name='rate')
    fig = px.line(daily, x='date', y='rate', labels={'date':'Date', 'rate':'Replacement Rate'}, title='Replacement Rate Over Time')
    st.plotly_chart(fig, use_container_width=True)

def domain_breakdown_chart(df: pd.DataFrame):
    """Bar chart of replacements by domain."""
    domain_counts = df[df['action'] == 'replaced']['domain'].value_counts().reset_index()
    domain_counts.columns = ['domain', 'count']
    fig = px.bar(domain_counts, x='domain', y='count', title='Replacements by Domain')
    st.plotly_chart(fig, use_container_width=True)

def confidence_histogram(df: pd.DataFrame):
    """Histogram of Whisper confidence scores."""
    fig = px.histogram(df, x='whisper_confidence', nbins=20, title='Confidence Distribution')
    st.plotly_chart(fig, use_container_width=True)

def top_replacements(df: pd.DataFrame, top_n: int = 10):
    """Bar chart of most common replacement pairs."""
    pairs = (
        df[df['action'] == 'replaced']
        .groupby(['original_word', 'replacement_word'])
        .size()
        .reset_index(name='count')
    )
    top = pairs.nlargest(top_n, 'count')
    top['pair'] = top['original_word'] + ' → ' + top['replacement_word']
    fig = px.bar(top, x='pair', y='count', title=f'Top {top_n} Replacements')
    st.plotly_chart(fig, use_container_width=True)
