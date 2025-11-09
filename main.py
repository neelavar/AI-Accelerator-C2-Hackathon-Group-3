"""
MediScout - Multi-Agent AI Medical Researcher
Main Streamlit Application
"""

import os
import sys
from pathlib import Path
from typing import List

import streamlit as st
from loguru import logger
from langchain_core.runnables import RunnableConfig

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mediscout.config import get_settings
from mediscout.orchestrator import ResearchOrchestrator
from mediscout.streamlit_callback import StreamlitCallbackHandler


# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")

# Page config
st.set_page_config(
    page_title="MediScout - AI Medical Researcher",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = None
    if "indexed_files" not in st.session_state:
        st.session_state.indexed_files = []
    if "report_generated" not in st.session_state:
        st.session_state.report_generated = False
    if "final_report" not in st.session_state:
        st.session_state.final_report = None


def load_orchestrator():
    """Load the research orchestrator (with caching)."""
    if st.session_state.orchestrator is None:
        with st.spinner("🔄 Initializing MediScout AI system..."):
            try:
                st.session_state.orchestrator = ResearchOrchestrator()
                st.success("✅ MediScout initialized successfully!")
            except Exception as e:
                st.error(f"❌ Failed to initialize: {e}")
                st.stop()
    
    return st.session_state.orchestrator


def sidebar_setup():
    """Render the sidebar with configuration info."""
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=MediScout", width=150)
        st.title("MediScout")
        st.caption("Multi-Agent AI Medical Researcher")
        
        st.divider()
        
        settings = get_settings()
        
        st.subheader("⚙️ Configuration")
        
        # API Status
        if settings.has_openrouter_key:
            st.success("✅ OpenRouter API Key")
        else:
            st.error("❌ OpenRouter API Key Missing")
            st.caption("Add OPENROUTER_API_KEY to .env file")
        
        if settings.langsmith_enabled:
            st.success("✅ LangSmith Tracing")
        else:
            st.info("ℹ️ LangSmith Tracing Disabled")
        
        st.divider()
        
        st.subheader("📊 Statistics")
        
        if st.session_state.orchestrator:
            retriever = st.session_state.orchestrator.get_retriever()
            stats = retriever.knowledge_base.get_collection_stats()
            
            st.metric("Indexed Chunks", stats["total_chunks"])
            st.metric("Indexed Files", len(st.session_state.indexed_files))
        
        st.divider()
        
        st.subheader("ℹ️ About")
        st.caption("""
        MediScout automates medical literature research using specialized AI agents:
        
        - 🔍 Query Validator
        - 📚 Document Retriever  
        - 🔬 Critical Analyzer
        - 📝 Report Builder
        
        **Version:** 0.1.0 (MVP)
        """)


def section_knowledge_base():
    """Render the knowledge base setup section."""
    st.header("📚 Step 1: Setup Knowledge Base")
    st.caption("Upload your research documents (PDF, TXT) to build a searchable knowledge base")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Upload Documents",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            help="Upload medical research papers, articles, or notes"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        index_button = st.button("📥 Index Documents", use_container_width=True, type="primary")
    
    if index_button and uploaded_files:
        orchestrator = load_orchestrator()
        retriever = orchestrator.get_retriever()
        
        with st.spinner("🔄 Indexing documents..."):
            temp_dir = Path("./data/temp_uploads")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            file_paths = []
            for uploaded_file in uploaded_files:
                file_path = temp_dir / uploaded_file.name
                file_path.write_bytes(uploaded_file.read())
                file_paths.append(str(file_path))
            
            try:
                results = retriever.ingest_documents(file_paths)
                
                # Update session state
                for success in results["successful"]:
                    if success["file"] not in st.session_state.indexed_files:
                        st.session_state.indexed_files.append(success["file"])
                
                # Show results
                if results["successful"]:
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>✅ Successfully indexed {len(results['successful'])} document(s)</strong><br>
                        Total chunks: {results['total_chunks']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("📋 View indexed files"):
                        for item in results["successful"]:
                            st.write(f"✓ {Path(item['file']).name} ({item['chunks']} chunks)")
                
                if results["failed"]:
                    st.markdown(f"""
                    <div class="error-box">
                        <strong>❌ Failed to index {len(results['failed'])} document(s)</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("⚠️ View errors"):
                        for item in results["failed"]:
                            st.write(f"✗ {Path(item['file']).name}: {item['error']}")
            
            except Exception as e:
                st.error(f"❌ Indexing failed: {e}")
            
            finally:
                # Cleanup temp files
                for fp in file_paths:
                    Path(fp).unlink(missing_ok=True)
    
    elif index_button:
        st.warning("⚠️ Please upload at least one document first")
    
    # Show indexed files
    if st.session_state.indexed_files:
        with st.expander("📁 Currently Indexed Documents", expanded=False):
            for file_path in st.session_state.indexed_files:
                st.write(f"✓ {Path(file_path).name}")


def section_document_manager():
    """Render the document management section with preview and chunks."""
    st.header("📚 Document Manager")
    st.caption("View, preview, and explore your indexed documents and chunks")
    
    try:
        from mediscout.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        
        # Get all documents
        documents = kb.get_all_documents()
        
        if not documents:
            st.info("📭 No documents indexed yet. Upload and index documents in the Research Workflow tab first.")
            return
        
        st.success(f"📊 **{len(documents)} documents indexed** with {kb.get_collection_stats()['total_chunks']} total chunks")
        
        # Document selector
        doc_options = {doc['filename']: doc for doc in documents}
        selected_filename = st.selectbox(
            "Select a document to view",
            options=list(doc_options.keys()),
            help="Choose a document to preview its contents and chunks"
        )
        
        if selected_filename:
            selected_doc = doc_options[selected_filename]
            doc_id = selected_doc['document_id']
            chunk_count = selected_doc['chunk_count']
            
            st.divider()
            
            # Document info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Document ID", doc_id[:12] + "...")
            with col2:
                st.metric("Total Chunks", chunk_count)
            with col3:
                st.metric("Filename", selected_filename)
            
            # Get chunks
            chunks = kb.get_document_chunks(doc_id)
            
            if not chunks:
                st.warning("No chunks found for this document.")
                return
            
            # View mode selector
            view_mode = st.radio(
                "View Mode",
                options=["preview", "chunks", "search"],
                format_func=lambda x: {
                    "preview": "📄 Full Preview (First 5 chunks)",
                    "chunks": "🧩 All Chunks (Detailed)",
                    "search": "🔍 Search Within Document"
                }[x],
                horizontal=True
            )
            
            if view_mode == "preview":
                st.subheader("📄 Document Preview")
                st.caption("Showing first 5 chunks to preview the document")
                
                preview_chunks = chunks[:5]
                for chunk in preview_chunks:
                    with st.expander(f"Chunk {chunk['chunk_index'] + 1} of {chunk_count}", expanded=False):
                        st.text_area(
                            "Content",
                            value=chunk['content'],
                            height=150,
                            key=f"preview_{chunk['chunk_id']}",
                            disabled=True
                        )
                
                if len(chunks) > 5:
                    st.info(f"💡 Showing 5 of {len(chunks)} chunks. Switch to 'All Chunks' view to see everything.")
            
            elif view_mode == "chunks":
                st.subheader("🧩 All Document Chunks")
                st.caption(f"Viewing all {len(chunks)} chunks")
                
                # Pagination
                chunks_per_page = 10
                total_pages = (len(chunks) + chunks_per_page - 1) // chunks_per_page
                
                page = st.selectbox(
                    "Page",
                    options=list(range(1, total_pages + 1)),
                    format_func=lambda x: f"Page {x} of {total_pages}"
                )
                
                start_idx = (page - 1) * chunks_per_page
                end_idx = min(start_idx + chunks_per_page, len(chunks))
                page_chunks = chunks[start_idx:end_idx]
                
                for chunk in page_chunks:
                    with st.expander(f"📄 Chunk {chunk['chunk_index'] + 1}", expanded=False):
                        st.markdown(f"**Chunk ID:** `{chunk['chunk_id']}`")
                        st.markdown(f"**Size:** {len(chunk['content'])} characters")
                        st.text_area(
                            "Content",
                            value=chunk['content'],
                            height=200,
                            key=f"chunk_{chunk['chunk_id']}",
                            disabled=True
                        )
            
            elif view_mode == "search":
                st.subheader("🔍 Search Within This Document")
                
                search_query = st.text_input(
                    "Search Query",
                    placeholder="Enter keywords to search in this document...",
                    help="Find specific sections or concepts within this document"
                )
                
                if search_query:
                    # Simple keyword search through chunks
                    matching_chunks = []
                    for chunk in chunks:
                        if search_query.lower() in chunk['content'].lower():
                            matching_chunks.append(chunk)
                    
                    if matching_chunks:
                        st.success(f"✅ Found {len(matching_chunks)} matching chunks")
                        
                        for chunk in matching_chunks:
                            with st.expander(f"🎯 Chunk {chunk['chunk_index'] + 1} - Match Found", expanded=True):
                                # Highlight matching text
                                content = chunk['content']
                                # Simple highlight by showing context
                                query_pos = content.lower().find(search_query.lower())
                                if query_pos >= 0:
                                    start = max(0, query_pos - 100)
                                    end = min(len(content), query_pos + len(search_query) + 100)
                                    context = content[start:end]
                                    
                                    st.markdown(f"**Match Context:**")
                                    st.markdown(f"...{context}...")
                                    st.divider()
                                
                                st.text_area(
                                    "Full Content",
                                    value=content,
                                    height=150,
                                    key=f"search_{chunk['chunk_id']}",
                                    disabled=True
                                )
                    else:
                        st.warning(f"No matches found for '{search_query}'")
    
    except Exception as e:
        st.error(f"❌ Error loading documents: {e}")
        logger.exception("Document manager error")


def section_research():
    """Render the research execution section."""
    st.header("🔬 Step 2: Conduct Research")
    st.caption("Enter your research question and let MediScout analyze the literature")
    
    # Research topic input
    research_topic = st.text_area(
        "Research Topic",
        placeholder="e.g., Efficacy of metformin for type 2 diabetes prevention",
        height=100,
        help="Enter a specific medical research question"
    )
    
    # Search scope options - IMPROVED
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_scope = st.radio(
            "Choose Your Search Sources:",
            options=["pubmed_only", "local_and_pubmed", "local_only"],
            format_func=lambda x: {
                "pubmed_only": "🌐 PubMed Only - Latest published medical research (Recommended)",
                "local_and_pubmed": "🔬 Both Local + PubMed - Comprehensive search (Slower)",
                "local_only": "📁 Local Documents Only - Your uploaded files (Fast)"
            }[x],
            index=0,  # Default to PubMed only
            help="PubMed searches millions of medical articles. Local search uses your uploaded documents."
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        generate_button = st.button("🚀 Generate Report", use_container_width=True, type="primary")
    
    # Show clear info based on search scope
    if search_scope == "local_only":
        st.warning("⚡ **Searching Your Uploads Only** - Make sure you've uploaded relevant PDFs in Step 1. No external sources will be used.")
    elif search_scope == "pubmed_only":
        st.success("🌐 **Searching PubMed Database** - Will search millions of published medical articles. Expected time: ~10-13 seconds.")
    else:
        st.info("🔍 **Comprehensive Search** - Will search both your local documents AND PubMed. Expected time: ~12-15 seconds.")
    
    if generate_button and research_topic:
        orchestrator = load_orchestrator()
        
        st.divider()
        
        # Status container
        status_container = st.container()
        
        with status_container:
            st.subheader("⚙️ Research Progress")
        
        # Create callback handler
        callback_handler = StreamlitCallbackHandler(status_container)
        config = RunnableConfig(callbacks=[callback_handler])
        
        try:
            # Run research workflow
            with st.spinner("🔄 Running research workflow..."):
                final_state = orchestrator.run_research(
                    research_topic=research_topic,
                    search_scope=search_scope,
                    config=config
                )
            
            # Check for errors
            if final_state.get("error_message"):
                st.error(f"❌ Research failed: {final_state['error_message']}")
            
            # Display results
            if final_state.get("final_report_markdown"):
                st.session_state.final_report = final_state["final_report_markdown"]
                st.session_state.report_generated = True
                
                st.success(f"""
                ✅ Research complete! 
                Analyzed {len(final_state.get('retrieved_documents', []))} documents 
                in {final_state.get('processing_time_seconds', 0):.1f} seconds
                """)
                
                st.divider()
                
                # Display report
                st.subheader("📄 Research Report")
                st.markdown(final_state["final_report_markdown"])
                
                # Download button
                st.download_button(
                    label="⬇️ Download Report (Markdown)",
                    data=final_state["final_report_markdown"],
                    file_name=f"mediscout_report_{research_topic[:30].replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                
                # Show retrieved documents with matching sections - IMPROVED
                st.divider()
                retrieved_docs = final_state.get('retrieved_documents', [])
                if retrieved_docs:
                    # Separate by source type
                    local_docs = [d for d in retrieved_docs if d.source == "user"]
                    pubmed_docs = [d for d in retrieved_docs if d.source == "pubmed"]
                    
                    st.subheader(f"📚 Retrieved Sources ({len(retrieved_docs)} total)")
                    
                    # Summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Sources", len(retrieved_docs))
                    with col2:
                        st.metric("Local Documents", len(local_docs))
                    with col3:
                        st.metric("PubMed Articles", len(pubmed_docs))
                    
                    st.divider()
                    
                    # Show PubMed articles first (more prominent)
                    if pubmed_docs:
                        st.markdown("### 🌐 PubMed Articles (External Research)")
                        for i, doc in enumerate(pubmed_docs, 1):
                            with st.expander(f"📄 Article {i}: {doc.title}", expanded=(i==1)):
                                # Citation info
                                st.markdown(f"**Title:** {doc.title}")
                                if doc.metadata:
                                    if doc.metadata.get('authors'):
                                        st.markdown(f"**Authors:** {doc.metadata['authors']}")
                                    if doc.metadata.get('journal'):
                                        st.markdown(f"**Journal:** {doc.metadata['journal']}")
                                    if doc.metadata.get('pub_date'):
                                        st.markdown(f"**Published:** {doc.metadata['pub_date']}")
                                    if doc.metadata.get('pmid'):
                                        st.markdown(f"**PMID:** [{doc.metadata['pmid']}](https://pubmed.ncbi.nlm.nih.gov/{doc.metadata['pmid']}/)")
                                
                                st.markdown(f"**Relevance Score:** {doc.relevance_score:.2%}")
                                
                                st.markdown("**Abstract:**")
                                st.text_area(
                                    "Content",
                                    value=doc.content[:2000] + ("..." if len(doc.content) > 2000 else ""),
                                    height=200,
                                    key=f"pubmed_{i}_{doc.id}",
                                    disabled=True,
                                    label_visibility="collapsed"
                                )
                    
                    # Show local documents
                    if local_docs:
                        st.markdown("### 📁 Local Knowledge Base Documents")
                        for i, doc in enumerate(local_docs, 1):
                            with st.expander(f"📄 Document {i}: {doc.title}", expanded=(i==1 and not pubmed_docs)):
                                st.markdown(f"**Source:** {doc.title}")
                                st.markdown(f"**Relevance Score:** {doc.relevance_score:.2%}")
                                
                                st.markdown("**Matching Section:**")
                                st.text_area(
                                    "Content",
                                    value=doc.content[:1500] + ("..." if len(doc.content) > 1500 else ""),
                                    height=200,
                                    key=f"local_{i}_{doc.id}",
                                    disabled=True,
                                    label_visibility="collapsed"
                                )
        
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
            logger.exception("Research workflow failed")
    
    elif generate_button:
        st.warning("⚠️ Please enter a research topic first")


def main():
    """Main application entry point."""
    initialize_session_state()
    
    # Header
    st.markdown('<p class="main-header">🔬 MediScout</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Multi-Agent AI Medical Researcher</p>', unsafe_allow_html=True)
    
    # Sidebar
    sidebar_setup()
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["🏠 Research Workflow", "📚 Document Manager", "📖 User Guide"])
    
    with tab1:
        section_knowledge_base()
        st.divider()
        section_research()
    
    with tab2:
        section_document_manager()
    
    with tab3:
        st.markdown("""
        ## 📖 How to Use MediScout
        
        ### Step 1: Setup Knowledge Base
        1. Click **"Upload Documents"** and select PDF or TXT files
        2. Click **"Index Documents"** to process and store them
        3. Wait for confirmation that documents are indexed
        
        ### Step 2: Conduct Research
        1. Enter your research question in the text area
        2. Click **"Generate Report"** to start the analysis
        3. Wait while MediScout:
           - Validates your query
           - Retrieves relevant documents from your knowledge base and PubMed
           - Performs critical analysis of all sources
           - Compiles a comprehensive research report
        4. Review the generated report
        5. Download the report in Markdown format
        
        ### Tips for Best Results
        - **Be Specific:** Include drug names, diseases, or specific interventions
        - **Use Medical Terms:** The system works best with proper medical terminology
        - **Upload Relevant Documents:** More context leads to better insights
        - **Review Sources:** Always validate AI-generated insights with primary sources
        
        ### Example Queries
        - "Efficacy of metformin for type 2 diabetes prevention"
        - "Safety profile of mRNA COVID-19 vaccines in elderly patients"
        - "Treatment options for stage 3 chronic kidney disease"
        - "Biomarkers for early detection of Alzheimer's disease"
        
        ### Disclaimer
        ⚠️ MediScout is a research assistance tool only. It should not be used for clinical
        decision-making or as a substitute for professional medical advice.
        """)


if __name__ == "__main__":
    main()
