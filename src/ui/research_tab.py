import streamlit as st
from src.orchestrator import generate_research_report
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
            
            try:
                status_container = st.empty()
                st_callback = StreamlitCallbackHandler(status_container)
                
                final_report = generate_research_report(research_topic, st_callback)
                
                status_container.success("Report generation complete!")
                
                st.markdown(final_report)
                
                st.download_button(
                    label="Download Report",
                    data=final_report,
                    file_name=f"report_{research_topic.replace(' ', '_')}.md",
                    mime="text/markdown",
                )
                
            except Exception as e:
                error_msg = str(e)
                status_container.error(f"Error generating report: {error_msg}")
                st.error("Failed to generate report. Please try again or contact support if the problem persists.")
