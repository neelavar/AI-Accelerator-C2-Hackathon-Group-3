# MediScout Setup & Execution Guide

## Quick Start (1-Hour Development Timeline)

### Step 0: Prerequisites Check (2 minutes)

```bash
# Verify Python version
python --version  # Should be 3.11+

# Verify uv is installed
uv --version

# Verify git status
git status
```

### Step 1: Environment Setup (5 minutes)

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Create .env file from template
cp .env.example .env

# 3. Edit .env file and add your API keys
nano .env  # or use your preferred editor

# Required variables:
# OPENROUTER_API_KEY=your_key_here
# LANGCHAIN_API_KEY=your_langsmith_key_here (optional but recommended)
# LANGCHAIN_TRACING_V2=true
```

**Example .env file:**
```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
LLM_FAST_MODEL=google/gemma-2-9b-it:free
LLM_SMART_MODEL=meta-llama/llama-3.1-70b-instruct:free
TEMPERATURE=0.0

LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls_xxxxxxxxxxxxx
LANGCHAIN_PROJECT=mediscout-mvp

PUBMED_EMAIL=your.email@example.com
```

### Step 2: Install Dependencies (10 minutes)

```bash
# Compile requirements
uv pip compile pyproject.toml -o requirements.txt

# Install all dependencies
uv pip install -r requirements.txt

# Install project in editable mode
uv pip install -e .

# Verify installation
python -c "from mediscout.config import get_settings; print('✓ Installation successful')"
```

### Step 3: Run Unit Tests (5 minutes)

```bash
# Run all unit tests
pytest tests/test_config.py -v
pytest tests/test_schemas.py -v
pytest tests/test_knowledge_base.py -v

# Run all tests together
pytest tests/ -v --tb=short
```

### Step 4: Test Components Individually (10 minutes)

#### Test 4.1: Knowledge Base
```bash
# Create a test document
echo "This is a medical research study about diabetes treatment with metformin. The study shows significant improvement in glucose control." > test_doc.txt

# Ingest the document
python scripts/ingest_sample_docs.py test_doc.txt

# Expected output:
# ✓ Successful: 1
# 📦 Total chunks: X
```

#### Test 4.2: Document Retrieval
```bash
# Test retrieval from knowledge base and PubMed
python scripts/test_retrieval.py "diabetes treatment metformin"

# Expected output:
# - Knowledge base results (if documents uploaded)
# - PubMed results (requires internet)
```

#### Test 4.3: Full Orchestrator
```bash
# Test complete workflow
python scripts/test_orchestrator.py "efficacy of metformin for type 2 diabetes"

# Expected output:
# - Query validation results
# - Retrieved documents count
# - Analysis results
# - Final report saved to test_report.md
```

### Step 5: Run Streamlit UI (5 minutes)

```bash
# Launch the Streamlit application
streamlit run main.py

# Browser should open automatically at http://localhost:8501
# If not, manually navigate to the URL shown in terminal
```

### Step 6: Integration Testing (15 minutes)

```bash
# Run integration tests (requires API keys)
pytest tests/test_integration.py -v -m integration

# Run all tests including slow ones
pytest tests/ -v
```

### Step 7: End-to-End Verification (10 minutes)

**Through Streamlit UI:**

1. **Upload Documents**:
   - Create or use sample PDFs/TXT files
   - Click "Upload Documents"
   - Click "Index Documents"
   - Verify success message

2. **Run Research**:
   - Enter query: "efficacy of metformin for diabetes prevention"
   - Click "Generate Report"
   - Watch progress updates
   - Verify report generation

3. **Download Report**:
   - Click "Download Report"
   - Verify Markdown file is complete

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Issue: ModuleNotFoundError
# Solution: Ensure virtual environment is activated
source .venv/bin/activate
uv pip install -e .
```

#### 2. ChromaDB Errors
```bash
# Issue: ChromaDB connection or permission errors
# Solution: Delete and recreate the database
rm -rf data/chromadb
python -c "from mediscout.knowledge_base import KnowledgeBase; kb = KnowledgeBase()"
```

#### 3. API Key Errors
```bash
# Issue: OpenRouter authentication failed
# Solution: Verify .env file
cat .env | grep OPENROUTER_API_KEY
# Ensure key starts with "sk-or-v1-"
```

#### 4. PubMed Rate Limiting
```bash
# Issue: Too many requests error
# Solution: Wait 1 minute, then add API key to .env
# PUBMED_API_KEY=your_ncbi_api_key
```

#### 5. Embedding Model Download
```bash
# Issue: Slow first run
# Solution: Model downloads on first use (~80MB)
# Wait for: "Loading embedding model: sentence-transformers/all-MiniLM-L6-v2"
# This is one-time only
```

## Testing Checklist

### Unit Tests ✓
- [x] Config module
- [x] Schemas validation
- [x] Knowledge base operations
- [x] Text extraction (PDF, TXT)
- [x] Embedding generation
- [x] Vector search

### Integration Tests ✓
- [x] Document ingestion workflow
- [x] PubMed API integration
- [x] Full orchestrator workflow
- [x] End-to-end with documents

### Manual Verification ✓
- [x] Streamlit UI loads
- [x] Document upload works
- [x] Indexing completes
- [x] Research query processes
- [x] Report generates
- [x] Download works
- [x] Progress updates display
- [x] Error handling graceful

## Performance Expectations

- **Document Indexing**: 5-10 seconds per PDF
- **Knowledge Base Search**: < 500ms
- **PubMed Search**: 2-5 seconds
- **Single Document Analysis**: 5-15 seconds
- **Full Report Generation**: 1-3 minutes (for 10-20 documents)

## File Structure Reference

```
mediscout/
├── src/mediscout/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── schemas.py             # Pydantic data models
│   ├── state.py               # LangGraph state
│   ├── knowledge_base.py      # Vector store & embeddings
│   ├── orchestrator.py        # Main workflow coordinator
│   ├── streamlit_callback.py  # UI progress updates
│   ├── agents/
│   │   ├── validate_query.py
│   │   ├── retriever.py
│   │   ├── critical_analysis.py
│   │   └── report_builder.py
│   └── services/
│       └── pubmed_client.py
├── tests/
│   ├── test_config.py
│   ├── test_schemas.py
│   ├── test_knowledge_base.py
│   └── test_integration.py
├── scripts/
│   ├── test_retrieval.py      # CLI: Test retrieval
│   ├── test_orchestrator.py   # CLI: Test full workflow
│   └── ingest_sample_docs.py  # CLI: Bulk document ingestion
├── main.py                     # Streamlit UI entry point
├── pyproject.toml             # Dependencies
├── requirements.txt           # Compiled requirements
└── .env                       # Your API keys (not in git)
```

## Next Steps After Verification

1. **Prepare Demo Data**: Create 3-5 sample PDFs on a medical topic
2. **Test Demo Flow**: Practice the complete workflow
3. **Monitor Logs**: Check for any warnings or errors
4. **Review Generated Reports**: Ensure quality meets requirements
5. **Optimize Performance**: Adjust chunk sizes if needed

## Support & Resources

- **LangSmith Dashboard**: https://smith.langchain.com/ (for tracing)
- **OpenRouter Dashboard**: https://openrouter.ai/activity (for usage)
- **PubMed API Docs**: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- **Project Issues**: Check logs in `logs/mediscout.log`

## Success Criteria Verification

- ✅ End-to-end workflow completes without errors
- ✅ User can upload documents and they are indexed
- ✅ PubMed retrieval returns relevant results
- ✅ Analysis extracts structured information
- ✅ Report is well-formatted and comprehensive
- ✅ All unit tests pass
- ✅ Integration tests pass
- ✅ UI is responsive and user-friendly
- ✅ Progress updates work in real-time
- ✅ Error messages are clear and actionable

