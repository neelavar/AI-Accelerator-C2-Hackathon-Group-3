# MediScout Setup Guide for Non-Anaconda Users

This guide is for developers who want to run MediScout **without Anaconda**, using standard Python and pip/uv.

---

## Prerequisites

### 1. Python Installation

**Required:** Python 3.11, 3.12, or 3.13 (NOT 3.10 or 3.14+)

**Check your Python version:**
```bash
python --version
# or
python3 --version
```

**Don't have Python 3.11-3.13?**

- **macOS:** Use [pyenv](https://github.com/pyenv/pyenv) or download from [python.org](https://www.python.org/downloads/)
  ```bash
  # Install pyenv
  brew install pyenv
  
  # Install Python 3.12
  pyenv install 3.12.2
  pyenv global 3.12.2
  ```

- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt update
  sudo apt install python3.12 python3.12-venv python3.12-dev
  ```

- **Windows:** Download installer from [python.org](https://www.python.org/downloads/)

### 2. Package Manager

**Option A: uv (Recommended - 10-100x faster)**
```bash
pip install uv
```

**Option B: pip (Standard)**
```bash
python -m pip install --upgrade pip
```

---

## Installation Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/neelavar/AI-Accelerator-C2-Hackathon-Group-3.git
cd AI-Accelerator-C2-Hackathon-Group-3
```

### Step 2: Create Virtual Environment

**Using venv (Python standard):**
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate  # On Windows
```

**Using uv (faster):**
```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate  # On Windows
```

**Verify activation:**
```bash
which python  # Should show path inside .venv
# On Windows: where python
```

### Step 3: Configure Environment Variables

**Copy the example configuration:**
```bash
cp .env.example .env
```

**Edit the .env file:**
```bash
nano .env  # or use your preferred editor (vim, code, etc.)
```

**Required settings:**
```bash
# 1. Get OpenRouter API key from: https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here

# 2. Set your email for PubMed API
PUBMED_EMAIL=your.email@example.com
```

**Optional but recommended:**
```bash
# Enable LangSmith tracing for debugging
# Get key from: https://smith.langchain.com/
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls-your-actual-key-here
LANGCHAIN_PROJECT=mediscout-dev
```

### Step 4: Install Dependencies

**Using uv (recommended):**
```bash
uv pip install -r requirements.txt
uv pip install -e .
```

**Using pip:**
```bash
pip install -r requirements.txt
pip install -e .
```

**Installation time:**
- With uv: ~2-3 minutes
- With pip: ~5-10 minutes

### Step 5: Verify Installation

**Test configuration:**
```bash
python -c "from mediscout.config import get_settings; print('✓ Config loaded successfully!')"
```

**Test imports:**
```bash
python -c "import streamlit; import langchain; import chromadb; print('✓ All dependencies loaded!')"
```

**Expected output:**
```
✓ Config loaded successfully!
✓ All dependencies loaded!
```

---

## Running the Application

### Option 1: Streamlit UI (Recommended)

```bash
streamlit run main.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Open your browser to `http://localhost:8501`

### Option 2: CLI Scripts

**Test document retrieval:**
```bash
python scripts/test_retrieval.py "diabetes treatment"
```

**Test orchestrator:**
```bash
python scripts/test_orchestrator.py "What are the latest treatments for type 2 diabetes?"
```

**Ingest sample documents:**
```bash
python scripts/ingest_sample_docs.py data/sample_papers/
```

---

## Testing

### Run Unit Tests

```bash
# Install dev dependencies first
pip install pytest pytest-asyncio pytest-mock

# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_config.py -v
pytest tests/test_knowledge_base.py -v
```

### Run Integration Tests

```bash
pytest tests/test_integration.py -v
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'mediscout'`

**Solution:**
```bash
# Ensure you're in the project root and virtual environment is activated
source .venv/bin/activate
pip install -e .
```

### Issue: `Cannot copy out of meta tensor; no data!`

**Solution:** Clear the embedding model cache:
```bash
rm -rf ~/.cache/torch/sentence_transformers/
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Issue: `Configuration Error: 'Settings' object has no attribute 'openrouter_api_key'`

**Solution:** Check your .env file:
```bash
# Ensure you have:
OPENROUTER_API_KEY=your_key_here  # NOT LLM_API_KEY
PUBMED_EMAIL=your.email@example.com
```

### Issue: Python version conflict

**Solution:** Use pyenv to manage Python versions:
```bash
pyenv install 3.12.2
pyenv local 3.12.2
python -m venv .venv
source .venv/bin/activate
```

### Issue: Slow dependency installation

**Solution:** Use uv instead of pip:
```bash
pip install uv
uv pip install -r requirements.txt
```

### Issue: Permission denied when creating directories

**Solution:** Ensure write permissions:
```bash
chmod -R u+w data/ logs/
# Or run with appropriate permissions
```

---

## System Requirements

### Minimum:
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disk:** 2 GB free space
- **OS:** macOS 10.13+, Ubuntu 18.04+, Windows 10+

### Recommended:
- **CPU:** 4+ cores
- **RAM:** 8 GB
- **Disk:** 5 GB free space (for model caching)
- **GPU:** Optional (for faster embeddings)

### Network:
- Internet connection required for:
  - PubMed API access
  - OpenRouter LLM API
  - LangSmith tracing (optional)
  - Model downloads (first run only)

---

## Common Configuration Options

### Use GPU for Embeddings

**Edit .env:**
```bash
EMBEDDING_DEVICE=cuda  # Requires CUDA-compatible GPU
```

**Install GPU-enabled PyTorch:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Use a Faster (Smaller) LLM Model

**Edit .env:**
```bash
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

### Adjust Chunk Size for Better Performance

**Edit .env:**
```bash
CHUNK_SIZE=1500          # Larger chunks = faster, less granular
CHUNK_OVERLAP=200        # More overlap = better context
TOP_K_RESULTS=3          # Fewer results = faster
```

### Disable LangSmith Tracing

**Edit .env:**
```bash
LANGCHAIN_TRACING_V2=false
```

---

## Development Workflow

### 1. Activate Environment (Every New Terminal)
```bash
source .venv/bin/activate
```

### 2. Make Code Changes
```bash
# Edit files in src/mediscout/
```

### 3. Run Tests
```bash
pytest tests/ -v
```

### 4. Run Application
```bash
streamlit run main.py
```

### 5. Check Logs
```bash
tail -f logs/mediscout.log
```

---

## Updating Dependencies

### Update All Dependencies
```bash
# Regenerate requirements.txt
uv pip compile pyproject.toml -o requirements.txt --upgrade

# Install updated dependencies
uv pip install -r requirements.txt
```

### Update Specific Package
```bash
pip install --upgrade langchain
```

---

## Uninstalling

### Remove Virtual Environment
```bash
deactivate  # Exit virtual environment
rm -rf .venv
```

### Remove Data and Logs
```bash
rm -rf data/ logs/ chromadb/
```

### Remove Model Cache
```bash
rm -rf ~/.cache/torch/sentence_transformers/
```

---

## Additional Resources

- **OpenRouter API Docs:** https://openrouter.ai/docs
- **LangChain Docs:** https://python.langchain.com/
- **LangSmith Docs:** https://docs.smith.langchain.com/
- **PubMed API Docs:** https://www.ncbi.nlm.nih.gov/home/develop/api/
- **ChromaDB Docs:** https://docs.trychroma.com/
- **Streamlit Docs:** https://docs.streamlit.io/

---

## Getting Help

1. **Check logs:** `tail -f logs/mediscout.log`
2. **Enable debug logging:** Set `LOG_LEVEL=DEBUG` in .env
3. **Enable LangSmith tracing:** Set `LANGCHAIN_TRACING_V2=true`
4. **Check GitHub Issues:** https://github.com/neelavar/AI-Accelerator-C2-Hackathon-Group-3/issues

---

**Happy researching! 🔬**

