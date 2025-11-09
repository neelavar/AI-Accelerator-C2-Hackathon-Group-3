import streamlit as st
import requests
from src.config import BACKEND_URL

def render_knowledge_base_tab():
    st.header("Manage Your Knowledge Base")
    st.markdown("Upload your internal research documents, papers, or data files to create a persistent knowledge base for the AI to use.")
    
    uploaded_files = st.file_uploader(
        "Upload Files (.pdf, .txt)",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    # Initialize session state for indexed documents (list of dicts)
    if "indexed_documents" not in st.session_state:
        st.session_state.indexed_documents = []
    if "preview_file_name" not in st.session_state:
        st.session_state.preview_file_name = None
    if "preview_content" not in st.session_state:
        st.session_state.preview_content = ""

    # Determine current uploaded file details for comparison
    current_uploaded_file_details = {(f.name, f.size) for f in uploaded_files} if uploaded_files else set()
    
    # Determine currently indexed file details for comparison
    current_indexed_file_details = {(doc['name'], doc['size']) for doc in st.session_state.indexed_documents}

    # Check if the file selection has changed and prompt the user to re-index
    if current_uploaded_file_details != current_indexed_file_details:
        st.info("Your document selection has changed. Click 'Sync & Index Knowledge Base' to update the knowledge base.")

    # Auto-Sync Checkbox (defaulting to False)
    auto_sync_enabled = st.checkbox("Enable Auto-Sync (re-indexes automatically on file changes)", value=False)

    # Sync & Index Button
    if st.button("Sync & Index Knowledge Base") or (auto_sync_enabled and current_uploaded_file_details != current_indexed_file_details):
        if uploaded_files:
            try:
                files = [("files", (f.name, f, f.type)) for f in uploaded_files]
                response = requests.post(
                    f"{BACKEND_URL}/api/knowledge_base/index",
                    files=files
                )
                response.raise_for_status()
                indexing_summary = response.json()
                summary_message = []
                if indexing_summary.get("newly_indexed_count", 0) > 0:
                    summary_message.append(f"{indexing_summary['newly_indexed_count']} new document(s) indexed.")
                if indexing_summary.get("updated_count", 0) > 0:
                    summary_message.append(f"{indexing_summary['updated_count']} document(s) updated.")
                if indexing_summary.get("skipped_count", 0) > 0:
                    summary_message.append(f"{indexing_summary['skipped_count']} document(s) skipped (already indexed).")
                if indexing_summary.get("removed_count", 0) > 0:
                    summary_message.append(f"{indexing_summary['removed_count']} document(s) removed from KB.")
                if summary_message:
                    st.success(" ".join(summary_message))
                else:
                    st.info("No changes detected in documents.")
                # Update indexed_files for research tab compatibility
                st.session_state.indexed_files = [f.name for f in uploaded_files]
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred during indexing: {e}")
        else:
            st.session_state.indexed_documents = []
            st.warning("No documents uploaded. Knowledge Base cleared.")
            st.rerun()

    # Document Workbench Display
    if st.session_state.indexed_documents:
        st.subheader("Your Document Workbench")
        # Add custom CSS for scrollable container and card styling
        st.markdown(
            """
            <style>
            .scrollable-container {
                max-height: 400px; /* Fixed height for scroll */
                overflow-y: auto;
                border: 1px solid #ddd;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 15px;
            }
            .document-card-compact {
                background-color: #f0f2f6;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
                display: flex;
                align-items: center; /* Align items vertically in the middle */
                justify-content: space-between; /* Space out content and buttons */
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .document-card-info {
                display: flex;
                flex-direction: column;
                flex-grow: 1; /* Allow info to take available space */
            }
            .document-card-header {
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: bold;
            }
            .document-card-status {
                font-size: 0.8em;
                color: green; /* Default to green for indexed */
            }
            .document-card-actions {
                display: flex;
                gap: 5px;
                /* No margin-top needed as it's now horizontal */
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Scrollable container for cards
        st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
        
        # Use st.columns for the grid layout
        cols = st.columns(3) 
        
        for i, doc in enumerate(st.session_state.indexed_documents):
            file_name = doc['name']
            file_size = doc['size']
            file_status = doc['status'] # e.g., 'indexed', 'updated'

            with cols[i % 3]: # Place cards in columns
                # Mock content for preview
                mock_preview_content = f"--- Preview of {file_name} ---\n\nThis is a mock preview content for the file '{file_name}'.\n\nFile Size: {file_size} bytes\nStatus: {file_status}\n\nIn a real implementation, this would show the actual extracted text from the document.\n\nLorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
                
                st.markdown(f"""
                <div class="document-card-compact">
                    <div class="document-card-info">
                        <div class="document-card-header">
                            📄 {file_name}
                        </div>
                        <span class="document-card-status">🟢 {file_status.capitalize()} ({file_size} bytes)</span>
                    </div>
                    <div class="document-card-actions">
                """, unsafe_allow_html=True)
                
                # Use st.columns for icon buttons to place them side-by-side
                button_cols = st.columns(2)
                with button_cols[0]:
                    if st.button("👁️", key=f"preview_{file_name}_{i}", help="Preview Document"):
                        st.session_state.preview_file_name = file_name
                        st.session_state.preview_content = mock_preview_content
                        st.rerun()
                with button_cols[1]:
                    if st.button("🗑️", key=f"remove_{file_name}_{i}", help="Remove Document"):
                        # Remove the document from the indexed_documents list
                        st.session_state.indexed_documents = [
                            d for d in st.session_state.indexed_documents if d['name'] != file_name
                        ]
                        st.success(f"'{file_name}' removed from selection. Click 'Sync & Index Knowledge Base' to update.")
                        st.rerun()
                
                st.markdown("</div></div>", unsafe_allow_html=True) # Close card actions and card div
        
        st.markdown('</div>', unsafe_allow_html=True) # Close scrollable container div

    # Render Preview Expander if requested
    if st.session_state.preview_file_name: # Check if a file is selected for preview
        with st.expander(f"👁️ Preview: {st.session_state.preview_file_name}", expanded=True):
            st.code(st.session_state.preview_content, language="text")
            if st.button("Close Preview", key="close_preview_expander"):
                st.session_state.preview_file_name = None
                st.session_state.preview_content = ""
                st.rerun()
