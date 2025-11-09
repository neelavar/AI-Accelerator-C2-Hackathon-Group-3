import streamlit as st
from src.mock_backend import mock_generate_report
from src.streamlit_callback import StreamlitCallbackHandler

def render_research_tab():
    st.header("Run Your Research")
    
    research_topic = st.text_input(
        "Enter your research topic",
        placeholder="e.g., Efficacy of drug X for condition Y"
    )

    if st.button("Generate Report"):
        if not research_topic:
            st.warning("Please enter a research topic.")
        elif not st.session_state.indexed_documents:
            st.warning("Please add documents to your knowledge base first in the 'Knowledge Base' tab.")
        else:
            st.subheader("Generated Report")
            
            status_container = st.empty()
            st_callback = StreamlitCallbackHandler(status_container)
            
            final_report = mock_generate_report(research_topic, st_callback)
            
            status_container.success("Report generation complete!")
            
            st.markdown(final_report)
            
            st.download_button(
                label="Download Report",
                data=final_report,
                file_name=f"report_{research_topic.replace(' ', '_')}.md",
                mime="text/markdown",
            )
