import streamlit as st
import tempfile
import os
from src.knowledge_base import KnowledgeBase
from src.config import settings
from langchain_community.document_loaders import PyPDFLoader, TextLoader

def render_knowledge_base_tab():
    st.header("Manage Your Knowledge Base")
    st.markdown("Upload your internal research documents, papers, or data files to create a persistent knowledge base for the AI to use.")
    
    # Initialize KnowledgeBase in session state if not already initialized
    if 'kb' not in st.session_state:
        st.session_state.kb = KnowledgeBase()
    kb = st.session_state.kb

    uploaded_files = st.file_uploader(
        "Upload Files (.pdf, .txt)",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    # Initialize session state for indexed documents (list of dicts)
    if "indexed_documents" not in st.session_state:
        st.session_state.indexed_documents = []
    
    # Attempt to load existing documents from ChromaDB
    print("UI: Attempting to load existing documents from Knowledge Base.")
    existing_docs = kb.get_all_document_metadata()
    print(f"UI: kb.get_all_document_metadata() returned {len(existing_docs)} documents.")
    
    # Update session state if documents exist in ChromaDB
    if existing_docs:
        st.session_state.indexed_documents = existing_docs
        if len(existing_docs) > 0:
            st.success(f"Loaded {len(existing_docs)} documents from Knowledge Base.")
    else:
        print("UI: No existing documents found in Knowledge Base or an error occurred.")
    if "preview_file_name" not in st.session_state:
        st.session_state.preview_file_name = None
    if "preview_content" not in st.session_state:
        st.session_state.preview_content = ""

    # Sync & Index Button
    if st.button("Sync & Index Knowledge Base"):
        indexing_summary = {
            "newly_indexed_count": 0,
            "updated_count": 0,
            "skipped_count": 0,
            "removed_count": 0
        }
        
        if uploaded_files:
            temp_file_paths = []
            file_info_for_kb = [] # New list to store (temp_path, original_name)
            extracted_contents = {} # To store extracted text for preview
            
            for uploaded_file in uploaded_files:
                # Save to a temporary file for KnowledgeBase ingestion
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_file_paths.append(tmp_file.name)
                    file_info_for_kb.append((tmp_file.name, uploaded_file.name)) # Store temp path and original name
                
                # Extract text content for preview
                file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                try:
                    if file_extension == ".pdf":
                        loader = PyPDFLoader(tmp_file.name)
                    elif file_extension == ".txt":
                        loader = TextLoader(tmp_file.name)
                    else:
                        extracted_contents[uploaded_file.name] = "Preview not available for this file type."
                        continue
                    
                    docs = loader.load()
                    full_text = "\n\n".join([doc.page_content for doc in docs])
                    extracted_contents[uploaded_file.name] = full_text
                except Exception as e:
                    extracted_contents[uploaded_file.name] = f"Error extracting text: {e}"

            try:
                with st.spinner(f"Processing {len(uploaded_files)} documents..."):
                    # Clear existing data
                    kb.clear_collection()
                    
                    # Add new documents and wait for confirmation
                    kb.add_documents(file_info_for_kb)
                    
                    # Give ChromaDB a moment to process
                    import time
                    time.sleep(2)  # Small delay to ensure processing completes
                    
                    # Verify documents were added by checking the KB
                    indexed_docs = kb.get_all_document_metadata()
                    print(f"Verification: Found {len(indexed_docs)} documents in KB after indexing")
                    
                    if indexed_docs:
                        st.session_state.indexed_documents = indexed_docs
                        indexing_summary["newly_indexed_count"] = len(uploaded_files)
                        st.success(f"{indexing_summary['newly_indexed_count']} document(s) successfully indexed.")
                    else:
                        st.error("Documents were not successfully indexed. Please try again.")
                        print("Error: No documents found in KB after attempted indexing")

            except Exception as e:
                st.error(f"An error occurred during indexing: {e}")
            finally:
                for path in temp_file_paths:
                    os.remove(path) # Clean up temporary files
        else:
            # Handle case where user clicks index with no files uploaded (clear KB)
            kb.clear_collection()
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
            file_content = doc['content'] # Get actual content

            with cols[i % 3]: # Place cards in columns
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
                        st.session_state.preview_content = file_content # Use actual content
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

    # Test Knowledge Base Retrieval Section
    st.subheader("Test Knowledge Base Retrieval")
    query_text = st.text_input("Enter your query here to test retrieval:", key="retrieval_query")
    
    if st.button("Retrieve Documents", key="retrieve_button"):
        if query_text:
            with st.spinner("Searching Knowledge Base..."):
                try:
                    retrieved_docs = kb.search(query_text)
                    if retrieved_docs:
                        st.success(f"Found {len(retrieved_docs)} relevant documents.")
                        for i, doc in enumerate(retrieved_docs):
                            with st.expander(f"Retrieved Document {i+1} (Source: {doc.metadata.get('source_file', 'N/A')})"):
                                st.write(doc.page_content)
                                st.json(doc.metadata)
                    else:
                        st.info("No documents found matching your query.")
                except Exception as e:
                    st.error(f"Error during retrieval: {e}")
        else:
            st.warning("Please enter a query to retrieve documents.")
