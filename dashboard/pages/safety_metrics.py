import streamlit as st
import plotly.express as px
from database import queries
from utils import alerts

def render():
    st.title("Safety & Guardrails")
    st.markdown("Monitor AI safety metrics to ensure the rescoring system isn't introducing systematic errors, bias, or semantic drift.")
    
    df = queries.get_decisions()
    
    active_alerts, safety_score = alerts.check_safety_metrics(df)
    
    # Overview Score
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Overall Safety Score", f"{safety_score}/100", 
                  delta="-20.5" if safety_score < 80 else None, 
                  delta_color="normal")
        st.write("Score algorithm takes into account replacement volume, false positive rate, and edge cases.")
        
    with col2:
        if active_alerts:
            st.error(f"{len(active_alerts)} Active Alert(s) Detected!")
        else:
            st.success("All systems operating within normal safety bounds.")
            
    st.markdown("---")
    
    st.subheader("Active Incidents & Alerts")
    if not active_alerts:
        st.info("No active incidents. The rescoring behavior is currently stable.")
    else:
        for alert in active_alerts:
            with st.expander(f"🚨 {alert['severity']}: {alert['type']}", expanded=(alert['severity'] == "Critical")):
                st.write(f"**Description:** {alert['description']}")
                st.write(f"**Recommended Action:** {alert['action']}")
                if st.button(f"Acknowledge Issue ({alert['type']})", key=alert['type']):
                    st.toast("Issue acknowledged. Logging incident...")
                    
    st.markdown("---")
    st.subheader("Safety Trends")
    
    # 1. User Approval trend
    st.write("**Detector: False Positive Drift**")
    if not df.empty and 'user_approved' in df.columns and "timestamp" in df.columns:
        reviewed = df.dropna(subset=['user_approved']).copy()
        if not reviewed.empty:
            reviewed['date'] = reviewed['timestamp'].dt.date
            daily_approval = reviewed.groupby('date')['user_approved'].mean().reset_index()
            daily_approval.columns = ['date', 'approval_rate']
            
            fig = px.line(daily_approval, x='date', y='approval_rate', title='User Approval Rate Over Time', range_y=[0, 1])
            # Add threshold line
            fig.add_hline(y=0.9, line_dash='dash', line_color='red', annotation_text='90% Target')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough feedback collected to plot approval drift.")
    else:
        st.info("No data available.")

    # 2. Rejection context analysis
    st.write("**Detector: Common Error Modes (Phonetic vs LM)**")
    if not df.empty and 'user_approved' in df.columns:
        rejected = df[df['user_approved'] == False]
        if not rejected.empty:
            fig2 = px.scatter(
                rejected, 
                x='phonetic_similarity', 
                y='improvement', 
                color='whisper_confidence',
                hover_data=['original_word', 'replacement_word'],
                title="Failed Replacements: Phonetic Sim vs LM Improvement"
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.caption("Look for clusters: if rejected replacements cluster at lower phonetic similarity but high LM improvement, the LM might be overriding acoustics too aggressively.")
        else:
            st.info("No rejected replacements found to analyze.")
