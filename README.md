# MediScout - Multi-Agent AI Medical Researcher 🏥🤖

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**An intelligent research assistant for medical literature analysis powered by multi-agent AI.**

MediScout helps researchers, clinicians, and medical professionals analyze scientific literature, extract insights, and generate evidence-based hypotheses - all while maintaining complete traceability to source documents.

---

## 🎯 **Key Features**

- **🔍 Multi-Source Retrieval** - Searches PubMed, ClinicalTrials.gov, and your private documents
- **🧠 Local Embeddings** - No API costs for vector search (sentence-transformers)
- **🤖 Free LLMs** - Uses OpenRouter's free models (Llama 3.1 70B)
- **📊 RAG Pipeline** - Retrieval-Augmented Generation for grounded responses
- **✅ Full Traceability** - Every claim cites source documents
- **💰 Cost: $0** - Completely free for Phase 1 (no API keys required for testing)

---

## 🚀 **Quick Start**

### Prerequisites

- Python 3.11+ ([Download](https://www.python.org/downloads/))
- Git
- 2GB free disk space

### Installation

```bash
# Clone the repository
git clone https://github.com/neelavar/AI-Accelerator-C2-Hackathon-Group-3.git
cd AI-Accelerator-C2-Hackathon-Group-3

# Switch to development branch
git checkout docs/saro-dev-process

# Install dependencies
pip install -e ".[dev]"

# Copy configuration template
cp config.env.template .env

# Edit .env and add your API keys (optional for testing)
```

### Configuration

Edit `.env` file:

```bash
# Required for LLM functionality (get free key at https://openrouter.ai/keys)
OPENROUTER_API_KEY=your_key_here

# Optional: For enhanced tracing
LANGSMITH_API_KEY=your_key_here
LANGSMITH_TRACING=false

# Required for PubMed (use your email)
PUBMED_EMAIL=your_email@example.com
```

---

## 🧪 **Testing (TDD Approach)**

We follow **Test-Driven Development**. All features have tests written first.

### Run All Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_domain_models.py -v

# Run only unit tests (fast)
pytest tests/ -m unit

# Skip slow tests
pytest tests/ -m "not slow"
```

### Test Coverage

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

---

## 📁 **Project Structure**

```
mediscout/
├── src/mediscout/          # Main application code
│   ├── models/             # Pydantic domain models
│   │   └── domain.py       # Document, Chunk, Report, etc.
│   ├── services/           # Core services
│   │   ├── text_extraction.py    # PDF/TXT extraction
│   │   ├── embedding_service.py  # Local embeddings (TODO)
│   │   └── vector_store.py       # ChromaDB wrapper (TODO)
│   ├── clients/            # External API clients
│   │   ├── pubmed.py       # PubMed API (TODO)
│   │   └── clinicaltrials.py     # ClinicalTrials.gov (TODO)
│   └── config.py           # Settings management
│
├── tests/                  # Test suite (TDD)
│   ├── test_domain_models.py       # ✅ Complete
│   ├── test_text_extraction.py    # ✅ Complete
│   └── ...                         # More tests coming
│
├── docs/                   # Documentation
│   ├── project-docs/       # Architecture, design docs
│   │   ├── architecture-mvp.md
│   │   ├── technical-design-mvp.md
│   │   └── *.drawio / *.svg       # Diagrams
│   └── ai-personas/        # AI development personas
│
├── pyproject.toml          # Project configuration
├── pytest.ini              # Test configuration
└── README.md               # This file
```

---

## 📚 **Sample Test Data**

### Where to Download Medical Research Papers

#### 1. **PubMed Central (Free Full-Text)**
- **URL:** https://www.ncbi.nlm.nih.gov/pmc/
- **Format:** PDF, TXT
- **How to download:**
  1. Search for a topic (e.g., "GIST prevention")
  2. Filter: "Free full text"
  3. Click paper → "PDF" or "TXT" button
  4. Save to `data/sample_docs/`

#### 2. **ClinicalTrials.gov (Trial Documents)**
- **URL:** https://clinicaltrials.gov/
- **Format:** TXT (study protocols)
- **How to download:**
  1. Search for condition (e.g., "Gastrointestinal Stromal Tumor")
  2. Click study → "Full Text View"
  3. Copy text to .txt file in `data/sample_docs/`

#### 3. **arXiv (Medical AI Papers)**
- **URL:** https://arxiv.org/list/q-bio/recent
- **Format:** PDF
- **Categories:** Quantitative Biology (q-bio)

#### 4. **bioRxiv (Preprints)**
- **URL:** https://www.biorxiv.org/
- **Format:** PDF
- **Free and Open Access**

### Recommended Test Papers

Create `data/sample_docs/` directory and add 3-5 papers:

```bash
mkdir -p data/sample_docs

# Example papers to search for:
# 1. "SSRIs and gastrointestinal stromal tumors" (PubMed)
# 2. "c-KIT mutations in GIST" (PubMed Central)
# 3. Any clinical trial on GIST treatment (ClinicalTrials.gov)
```

---

## 🛠️ **Development (Phase 1 Status)**

### ✅ Completed
- [x] Project structure setup
- [x] Pydantic domain models with full validation
- [x] Text extraction service (PDF/TXT)
- [x] Configuration management
- [x] Unit tests for models and extraction
- [x] TDD test framework

### 🚧 In Progress (Next Steps)
- [ ] Text chunking service
- [ ] Embedding service (sentence-transformers)
- [ ] ChromaDB vector store wrapper
- [ ] PubMed API client
- [ ] ClinicalTrials.gov API client
- [ ] LLM service (OpenRouter)
- [ ] Basic RAG pipeline
- [ ] CLI interface

---

## 📖 **Documentation**

- **Architecture:** `docs/project-docs/architecture-mvp.md`
- **Technical Design:** `docs/project-docs/technical-design-mvp.md`
- **Domain Model:** `docs/project-docs/domain-model.md`
- **Technology Decisions:** `docs/project-docs/technology-decisions-rationale.md`
- **Diagrams:** `docs/project-docs/*.svg` (open in browser)

---

## 🤝 **Contributing**

We follow TDD principles:

1. **Write tests first** - Define expected behavior
2. **Implement code** - Make tests pass
3. **Refactor** - Improve code quality
4. **Document** - Add docstrings and comments

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

---

## 💡 **Technology Stack**

| Component | Technology | License | Cost |
|-----------|-----------|---------|------|
| **Vector DB** | ChromaDB | Apache 2.0 | Free |
| **Embeddings** | sentence-transformers | Apache 2.0 | Free |
| **LLM** | OpenRouter (Llama 3.1 70B) | MIT | Free tier |
| **Orchestration** | LangGraph | MIT | Free |
| **UI Framework** | Streamlit (planned) | Apache 2.0 | Free |
| **APIs** | PubMed, ClinicalTrials.gov | N/A | Free |
| **Tracing** | LangSmith (optional) | Proprietary | Free 5K traces/month |

**Total Cost:** $0 for Phase 1 development and testing

---

## 📧 **Contact & Support**

- **Repository:** [GitHub](https://github.com/neelavar/AI-Accelerator-C2-Hackathon-Group-3)
- **Branch:** `docs/saro-dev-process`
- **Issues:** Create a GitHub issue
- **Team:** AI Accelerator C2 - Group 3

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎓 **Acknowledgments**

- **AI Accelerator Programme C2 Cohort** - For the hackathon opportunity
- **OpenRouter** - For free LLM access
- **LangChain Team** - For LangGraph and LangSmith
- **Chroma Team** - For ChromaDB
- **sentence-transformers** - For local embeddings

---

**Made with ❤️ by Team Group 3 | AI Accelerator C2 Hackathon**
