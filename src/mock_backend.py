import streamlit as st
import time
from src.streamlit_callback import StreamlitCallbackHandler # This will be needed by mock_generate_report

def mock_ingest_files(uploaded_files):
    """
    Simulates the file ingestion and indexing process with smart duplicate/update detection.
    Returns a dictionary with counts of newly indexed, updated, and skipped files.
    """
    summary = {
        "newly_indexed_count": 0,
        "updated_count": 0,
        "skipped_count": 0,
        "removed_count": 0 # This will be handled by the UI logic
    }

    if not uploaded_files:
        # If no files are uploaded, it means the KB is being cleared
        summary["removed_count"] = len(st.session_state.indexed_documents)
        st.session_state.indexed_documents = []
        return summary

    # Initialize indexed_documents if not present
    if "indexed_documents" not in st.session_state:
        st.session_state.indexed_documents = []

    # Create a temporary list to build the new state of indexed_documents
    new_indexed_documents_state = []
    
    # Keep track of files that were in the old indexed_documents but not in uploaded_files
    old_indexed_names = {doc['name'] for doc in st.session_state.indexed_documents}
    current_uploaded_names = {f.name for f in uploaded_files}
    
    # Identify removed files
    for doc_name in old_indexed_names:
        if doc_name not in current_uploaded_names:
            summary["removed_count"] += 1

    with st.spinner(f"Processing {len(uploaded_files)} documents..."):
        time.sleep(1) # Simulate initial processing time

        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_size = uploaded_file.size

            # Check if file already exists and if it's updated
            found_in_old_indexed = False
            for doc in st.session_state.indexed_documents:
                if doc['name'] == file_name:
                    found_in_old_indexed = True
                    if doc['size'] != file_size:
                        # File exists but content (size) has changed, treat as update
                        new_indexed_documents_state.append({'name': file_name, 'size': file_size, 'status': 'indexed'})
                        summary["updated_count"] += 1
                        st.toast(f"Updated: {file_name}")
                    else:
                        # File exists and is unchanged
                        new_indexed_documents_state.append(doc) # Keep the existing doc entry
                        summary["skipped_count"] += 1
                        st.toast(f"Skipped (already indexed): {file_name}")
                    break
            
            if not found_in_old_indexed:
                # New file
                new_indexed_documents_state.append({'name': file_name, 'size': file_size, 'status': 'indexed'})
                summary["newly_indexed_count"] += 1
                st.toast(f"Indexed: {file_name}")
            
            time.sleep(0.5) # Simulate per-file processing

    st.session_state.indexed_documents = new_indexed_documents_state
    return summary

def mock_generate_report(topic, callback_handler):
    """
    Simulates the entire agentic research and report generation process.
    """
    # Simulate a series of agent steps
    steps = [
        "Validate Query",
        "Knowledge Base Retriever",
        "Web Researcher (PubMed)",
        "Merge Contexts",
        "Validate Retrieved Data",
        "Critical Analysis Agent",
        "Report Builder Agent",
    ]
    for step in steps:
        callback_handler.on_chain_start({"name": step}, {})
        time.sleep(1.5) # Simulate work for each step

    # Return a hardcoded sample report
    return """
# Research Report: The Efficacy of Drug X for Condition Y

## 1. Executive Summary
This AI-generated report synthesizes information from user-provided documents and external sources regarding the efficacy of Drug X for treating Condition Y. The analysis indicates a generally positive correlation, though some conflicting results were noted, suggesting a need for further research into patient subgroups.

## 2. Detailed Findings
- **Source A (User Doc):** A 2022 study found that Drug X reduced symptoms by 40% in a cohort of 50 patients.
- **Source B (PubMed):** A large-scale clinical trial (n=1000) published in 2023 showed a statistically significantly improvement in patient outcomes compared to a placebo.

## 3. Contradictions & Gaps
- While most studies are positive, a smaller study from 2021 (Source C) found no significant benefit in patients over the age of 65. This highlights a potential gap in understanding the drug's efficacy across different age demographics.

## 4. Generated Hypotheses
1.  **Hypothesis:** The efficacy of Drug X in treating Condition Y may be dependent on the patient's genetic markers, explaining the varied results in different studies.

## 5. Sources
- Source A: [User Document] internal_study_2022.pdf
- Source B: [PubMed] PMID: 12345678
- Source C: [PubMed] PMID: 87654321
"""
