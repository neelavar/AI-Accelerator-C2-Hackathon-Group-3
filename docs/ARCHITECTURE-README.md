# MediScout System Architecture

## 📊 Architecture Diagram

**File:** `MediScout-Architecture.drawio`

### How to View

#### Option 1: Online (Recommended - Always Works!)
1. Go to **[https://app.diagrams.net/](https://app.diagrams.net/)** (formerly draw.io)
2. Click **"Open Existing Diagram"**
3. Click **"Open from Device"** or just drag the file
4. Select `MediScout-Architecture.drawio`
5. ✅ The diagram will load!

#### Option 2: VS Code Extension
1. Install the **Draw.io Integration** extension in VS Code
2. Right-click `MediScout-Architecture.drawio` → "Open With" → "Draw.io Editor"
3. View and edit directly in VS Code

#### Option 3: Desktop App
1. Download [draw.io Desktop](https://github.com/jgraph/drawio-desktop/releases)
2. Install and open the `.drawio` file

### Troubleshooting

**If you get "Unknown error":**
1. Make sure you're using the **latest version** of diagrams.net
2. Try **Option 1** (online) - it's most reliable
3. If dragging doesn't work, use File → Open → Select file
4. Clear browser cache and try again
5. The file is 17KB and valid XML - it should work!

**Alternative: View as Text**
- The file is readable XML
- You can open it in any text editor to see the structure
- All component names and relationships are visible

---

## 🏗️ Architecture Overview

### **Layers**

1. **User Interface Layer (Blue)**
   - Streamlit Web App
   - Progress Display with storytelling
   - Search Scope Selector (Local/PubMed/Combined)
   - Document Manager (Preview, Chunks, Search)
   - Results Display

2. **Orchestration Layer (Yellow)**
   - LangGraph-based workflow
   - State management
   - Agent coordination
   - Error handling

3. **Agent Layer (Red)**
   - **Validate Query Agent**: Fast path keyword detection + LLM validation
   - **Retriever Agent**: Parallel local KB + PubMed search
   - **Critical Analysis Agent**: Evidence synthesis
   - **Report Builder Agent**: Markdown report generation

4. **Knowledge Base Layer (Purple)**
   - Document processor (PDF/TXT extraction)
   - Embedding generator (all-MiniLM-L6-v2, cached singleton)
   - ChromaDB vector store

5. **External Services Layer (Green)**
   - OpenRouter API (Llama models)
   - PubMed API (NCBI E-utilities)
   - LangSmith (Observability)

6. **Configuration & Infrastructure (Gray)**
   - Pydantic Settings
   - Environment variables
   - Logging (Loguru)

---

## 🔄 Data Flow

### **Document Upload Flow**
```
User Upload → Document Processor → Chunking (1000 tokens) 
→ Embedding Generator (cached) → ChromaDB Vector Store
```

### **Research Query Flow**
```
1. User Query → Streamlit UI
2. Orchestrator receives query
3. Validate Query Agent (fast path or LLM)
4. Retriever Agent (parallel):
   - Local KB search (1.5s timeout, top-3)
   - PubMed search (2.5s timeout, top-3)
5. Critical Analysis Agent (Llama-3.1-70B)
6. Report Builder Agent (Markdown generation)
7. Results Display → User
```

### **Progress Updates** (Real-time)
```
Orchestrator → StreamlitCallbackHandler → Progress Bar UI
```

---

## 🚀 Tech Stack Summary

| Category | Technology |
|----------|------------|
| **Frontend** | Streamlit |
| **Backend** | Python 3.11-3.13 |
| **Orchestration** | LangGraph |
| **LLM Provider** | OpenRouter (Llama-3.2-3B, Llama-3.1-70B) |
| **Vector Database** | ChromaDB (Persistent) |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **External APIs** | PubMed (Bio.Entrez) |
| **Observability** | LangSmith |
| **Configuration** | Pydantic Settings |
| **Document Processing** | pypdf, httpx |
| **Logging** | Loguru |

---

## ⚡ Performance Optimizations

1. **Singleton Embedding Model**: Cached globally (saves 2-3s)
2. **Fast Path Validation**: Keyword-based auto-accept (saves 2-4s)
3. **Faster LLM**: 3B model for validation vs 70B
4. **Top-3 Results**: Reduced from 20 → 3 (85% less data)
5. **Parallel Search**: ThreadPoolExecutor with aggressive timeouts
6. **Larger Chunks**: 1000 tokens (50% fewer chunks)
7. **Optimized Encoding**: Batch processing, normalized embeddings

**Expected Performance:**
- Local-only: 1-2 seconds
- PubMed-only: 2-3 seconds
- Combined: 3-5 seconds

---

## 📂 Key Files

```
src/mediscout/
├── config.py                  # Pydantic settings
├── state.py                   # LangGraph state
├── schemas.py                 # Data models
├── orchestrator.py            # Workflow orchestration
├── knowledge_base.py          # Vector DB management
├── streamlit_callback.py      # Progress UI
├── agents/
│   ├── validate_query.py      # Query validation
│   ├── retriever.py           # Document retrieval
│   ├── critical_analysis.py   # Analysis agent
│   └── report_builder.py      # Report generation
└── services/
    └── pubmed_client.py       # PubMed API

main.py                        # Streamlit entry point
```

---

## 🎯 Design Principles

1. **Modularity**: Each agent is independent and testable
2. **Observability**: LangSmith tracing for all LLM calls
3. **Performance**: Optimized for speed (caching, parallelization)
4. **User Experience**: Real-time progress, clear feedback
5. **Flexibility**: Multiple search modes (local/online/both)
6. **Scalability**: Stateless agents, persistent storage

---

## 📊 Key Metrics

- **Search Speed**: 3-5 seconds (end-to-end)
- **Validation**: <1 second (fast path) or 2-3 seconds (LLM)
- **Retrieval**: 1.5s local + 2.5s PubMed (parallel)
- **Top Results**: 3 per source (6 total max)
- **Chunk Size**: 1000 tokens with 150 overlap
- **Embedding Dimension**: 384

---

For detailed setup instructions, see [SETUP.md](../SETUP.md)

