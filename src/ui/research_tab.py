import streamlit as st
import requests
from src.config import BACKEND_URL

def render_research_tab():
    st.header("Run Your Research")
    
    research_topic = st.text_input(
        "Enter your research topic",
        placeholder="e.g., Efficacy of drug X for condition Y"
    )

    if st.button("Generate Report"):
        if not research_topic:
            st.warning("Please enter a research topic.")
        elif not st.session_state.indexed_files:
            st.warning("Please add documents to your knowledge base first in the 'Knowledge Base' tab.")
        else:
            st.subheader("Generated Report")
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/research/report",
                    data={
                        "topic": research_topic,
                        "files": ",".join(st.session_state.indexed_files)
                    }
                )
                response.raise_for_status()
                final_report = response.json().get("report", "No report generated.")
                st.success("Report generation complete!")
                st.markdown(final_report)
                st.download_button(
                    label="Download Report",
                    data=final_report,
                    file_name=f"report_{research_topic.replace(' ', '_')}.md",
                    mime="text/markdown",
                )
            except Exception as e:
                st.error(f"An error occurred during report generation: {e}")
