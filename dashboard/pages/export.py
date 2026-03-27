import streamlit as st
from database import queries
import pandas as pd
from io import BytesIO

def render():
    st.title("Data Export & Reporting")
    st.markdown("Generate and download comprehensive reports for auditing and compliance.")
    
    st.subheader("1. Decision Audit Trail")
    st.markdown("Export a detailed log of all autonomous rescoring decisions.")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=None, key="export_start")
    with col2:
        end_date = st.date_input("End Date", value=None, key="export_end")
        
    action_filter = st.selectbox("Action Type", ["All", "replaced", "kept_original"])
    
    # Generate data
    if st.button("Preview Audit Data"):
        df = queries.get_decisions(
            start_date=start_date, 
            end_date=end_date, 
            action=None if action_filter == "All" else action_filter
        )
        st.dataframe(df.head(10))
        st.caption(f"Showing first 10 rows. Total rows available for export: {len(df)}")
        
        # Download buttons
        if not df.empty:
            c1, c2 = st.columns(2)
            with c1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name="decision_audit_trail.csv",
                    mime="text/csv",
                )
            with c2:
                json_data = df.to_json(orient="records", indent=2)
                st.download_button(
                    label="Download as JSON",
                    data=json_data,
                    file_name="decision_audit_trail.json",
                    mime="application/json",
                )
                
    st.markdown("---")
    
    st.subheader("2. Performance Report")
    st.markdown("Generate a PDF-equivalent summary of system performance (implemented here as HTML for quick export).")
    
    if st.button("Generate Performance Summary"):
        # For simplicity we generate a basic raw HTML or text summary based on queries
        df = queries.get_decisions()
        if not df.empty:
            total_words = int(df['total_words'].fillna(100).sum()) # Mock if missing
            words_rescored = len(df[df['action']=='replaced'])
            approval_rate = df['user_approved'].mean() * 100 if 'user_approved' in df.columns and not df['user_approved'].isna().all() else 0
            
            report = f"""
            # Rescoring Performance Report
            
            **Total Processed**: {total_words} words (approx)
            **Total Rescored**: {words_rescored} words
            **User Approval Rate**: {approval_rate:.1f}%
            
            *Report generated via Dashboard*
            """
            st.download_button(
                label="Download Text Report",
                data=report,
                file_name="performance_summary.txt",
                mime="text/plain",
            )
        else:
            st.warning("No data available to generate report.")
            
    st.markdown("---")
    
    st.subheader("3. Error Analysis Export")
    st.markdown("Export only flagged and rejected decisions for model retraining.")
    
    if st.button("Prepare Error Dataset"):
        df = queries.get_decisions()
        errors = df[(df['user_approved'] == False) | (df['flagged'] == True)]
        if not errors.empty:
            csv_errors = errors.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Error Data (CSV)",
                data=csv_errors,
                file_name="error_analysis_dataset.csv",
                mime="text/csv",
            )
        else:
            st.success("No errors found in the system! Incredible.")
