import streamlit as st
from src.ui.knowledge_base_tab import render_knowledge_base_tab
from src.ui.research_tab import render_research_tab

# --- Page Configuration ---
st.set_page_config(
    page_title="MediScout: AI Medical Researcher",
    page_icon="🩺",
    layout="wide"
)

# --- UI Rendering ---

st.title("🩺 MediScout: AI Medical Researcher")
st.markdown("Your AI-powered partner for deep medical research and hypothesis generation.")

# Initialize global session state variables if they don't exist
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []
if "indexed_file_names" not in st.session_state:
    st.session_state.indexed_file_names = set()

# --- Main Layout with Tabs ---
tab1, tab2 = st.tabs(["🧠 Knowledge Base", "🔍 Research & Analysis"])

with tab1:
    render_knowledge_base_tab()

with tab2:
    render_research_tab()

def main():
    # This function is now implicitly run by Streamlit's execution model.
    # The main script body acts as the entry point.
    pass

if __name__ == "__main__":
    # To run the app, use the command: `streamlit run main.py`
    main()
