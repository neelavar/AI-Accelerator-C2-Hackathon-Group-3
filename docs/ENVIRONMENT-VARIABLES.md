# Environment Variables Reference

This document maps **configuration settings** in `src/mediscout/config.py` to **environment variables** in `.env`.

---

## Quick Reference Table

| Config Attribute | Environment Variable | Type | Default | Required? |
|-----------------|---------------------|------|---------|-----------|
| `openrouter_api_key` | `OPENROUTER_API_KEY` | str | None | ✅ **YES** |
| `openrouter_model` | `OPENROUTER_MODEL` | str | `meta-llama/llama-3.1-70b-instruct:free` | No |
| `llm_temperature` | `LLM_TEMPERATURE` | float | 0.7 | No |
| `llm_max_tokens` | `LLM_MAX_TOKENS` | int | 4000 | No |
| `llm_timeout_seconds` | `LLM_TIMEOUT_SECONDS` | int | 15 | No |
| `langsmith_api_key` | `LANGCHAIN_API_KEY` | str | None | No (Optional) |
| `langsmith_project` | `LANGCHAIN_PROJECT` | str | `mediscout-dev` | No |
| `langsmith_tracing` | `LANGCHAIN_TRACING_V2` | bool | False | No |
| `chroma_persist_dir` | `CHROMA_PERSIST_DIR` | Path | `./data/chroma` | No |
| `chroma_collection_name` | `CHROMA_COLLECTION_NAME` | str | `mediscout_docs` | No |
| `embedding_model` | `EMBEDDING_MODEL` | str | `sentence-transformers/all-MiniLM-L6-v2` | No |
| `embedding_device` | `EMBEDDING_DEVICE` | str | `cpu` | No |
| `embedding_batch_size` | `EMBEDDING_BATCH_SIZE` | int | 32 | No |
| `embedding_dimension` | `EMBEDDING_DIMENSION` | int | 384 | No |
| `pubmed_email` | `PUBMED_EMAIL` | str | `user@example.com` | ✅ **YES** |
| `pubmed_max_results` | `PUBMED_MAX_RESULTS` | int | 10 | No |
| `clinicaltrials_max_results` | `CLINICALTRIALS_MAX_RESULTS` | int | 5 | No |
| `serpapi_key` | `SERPAPI_KEY` | str | None | No |
| `serpapi_max_results` | `SERPAPI_MAX_RESULTS` | int | 5 | No |
| `log_level` | `LOG_LEVEL` | str | `INFO` | No |
| `log_file` | `LOG_FILE` | Path | `./logs/mediscout.log` | No |
| `chunk_size` | `CHUNK_SIZE` | int | 1000 | No |
| `chunk_overlap` | `CHUNK_OVERLAP` | int | 150 | No |
| `max_document_size_mb` | `MAX_DOCUMENT_SIZE_MB` | int | 50 | No |
| `top_k_results` | `TOP_K_RESULTS` | int | 5 | No |
| `similarity_threshold` | `SIMILARITY_THRESHOLD` | float | 0.3 | No |
| `rerank_enabled` | `RERANK_ENABLED` | bool | True | No |

---

## Detailed Variable Descriptions

### LLM Provider (OpenRouter)

#### `OPENROUTER_API_KEY` ✅ **REQUIRED**
- **Type:** String
- **Purpose:** Your OpenRouter API key for accessing LLM models
- **Get it from:** https://openrouter.ai/keys
- **Example:** `OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### `OPENROUTER_MODEL`
- **Type:** String
- **Default:** `meta-llama/llama-3.1-70b-instruct:free`
- **Purpose:** LLM model to use for analysis and report generation
- **Options:**
  - `meta-llama/llama-3.1-70b-instruct:free` - Best quality (slower)
  - `meta-llama/llama-3.2-3b-instruct:free` - Fast (lower quality)
  - `google/gemma-2-9b-it:free` - Balanced
- **Example:** `OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free`

#### `LLM_TEMPERATURE`
- **Type:** Float (0.0 - 2.0)
- **Default:** 0.7
- **Purpose:** Controls creativity/randomness of LLM responses
  - 0.0 = Deterministic, factual
  - 0.7 = Balanced
  - 2.0 = Very creative
- **Example:** `LLM_TEMPERATURE=0.5`

#### `LLM_MAX_TOKENS`
- **Type:** Integer (100 - 100000)
- **Default:** 4000
- **Purpose:** Maximum length of LLM responses
- **Example:** `LLM_MAX_TOKENS=2000`

#### `LLM_TIMEOUT_SECONDS`
- **Type:** Integer (5 - 300)
- **Default:** 15
- **Purpose:** Timeout for LLM API calls (seconds)
- **Example:** `LLM_TIMEOUT_SECONDS=30`

---

### LangSmith Tracing (Optional)

#### `LANGCHAIN_TRACING_V2`
- **Type:** Boolean
- **Default:** False
- **Purpose:** Enable LangSmith observability and tracing
- **Note:** Must use `LANGCHAIN_` prefix (not `LANGSMITH_`)
- **Example:** `LANGCHAIN_TRACING_V2=true`

#### `LANGCHAIN_API_KEY`
- **Type:** String
- **Default:** None
- **Purpose:** Your LangSmith API key
- **Get it from:** https://smith.langchain.com/
- **Example:** `LANGCHAIN_API_KEY=ls-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### `LANGCHAIN_PROJECT`
- **Type:** String
- **Default:** `mediscout-dev`
- **Purpose:** Project name in LangSmith dashboard
- **Example:** `LANGCHAIN_PROJECT=my-research-project`

---

### PubMed API

#### `PUBMED_EMAIL` ✅ **REQUIRED**
- **Type:** String (email format)
- **Default:** `user@example.com`
- **Purpose:** Required by NCBI for PubMed API access
- **Note:** No registration needed, not validated
- **Example:** `PUBMED_EMAIL=researcher@university.edu`

#### `PUBMED_MAX_RESULTS`
- **Type:** Integer (1 - 100)
- **Default:** 10
- **Purpose:** Maximum number of PubMed articles to fetch per query
- **Example:** `PUBMED_MAX_RESULTS=5`

---

### Vector Database (ChromaDB)

#### `CHROMA_PERSIST_DIR`
- **Type:** Path
- **Default:** `./data/chroma`
- **Purpose:** Directory where ChromaDB stores embedded documents
- **Example:** `CHROMA_PERSIST_DIR=/var/data/mediscout/chroma`

#### `CHROMA_COLLECTION_NAME`
- **Type:** String
- **Default:** `mediscout_docs`
- **Purpose:** ChromaDB collection name for document storage
- **Example:** `CHROMA_COLLECTION_NAME=research_papers`

---

### Embedding Model

#### `EMBEDDING_MODEL`
- **Type:** String
- **Default:** `sentence-transformers/all-MiniLM-L6-v2`
- **Purpose:** Model for generating document embeddings
- **Options:**
  - `sentence-transformers/all-MiniLM-L6-v2` - Fast, 384 dims (recommended)
  - `sentence-transformers/all-mpnet-base-v2` - Slower, 768 dims (more accurate)
- **Example:** `EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2`

#### `EMBEDDING_DEVICE`
- **Type:** String
- **Default:** `cpu`
- **Options:** `cpu`, `cuda`, `mps` (Apple Silicon)
- **Purpose:** Device for embedding generation
- **Example:** `EMBEDDING_DEVICE=cuda`

#### `EMBEDDING_BATCH_SIZE`
- **Type:** Integer (1 - 256)
- **Default:** 32
- **Purpose:** Batch size for embedding generation (lower if OOM)
- **Example:** `EMBEDDING_BATCH_SIZE=16`

---

### Document Processing

#### `CHUNK_SIZE`
- **Type:** Integer (100 - 2000)
- **Default:** 1000
- **Purpose:** Characters per text chunk
- **Trade-off:** Larger = faster, fewer chunks; Smaller = more granular
- **Example:** `CHUNK_SIZE=1500`

#### `CHUNK_OVERLAP`
- **Type:** Integer (0 - 500)
- **Default:** 150
- **Purpose:** Overlap between chunks (preserves context)
- **Note:** Must be less than `CHUNK_SIZE`
- **Example:** `CHUNK_OVERLAP=200`

#### `MAX_DOCUMENT_SIZE_MB`
- **Type:** Integer (1 - 500)
- **Default:** 50
- **Purpose:** Maximum file size to process (MB)
- **Example:** `MAX_DOCUMENT_SIZE_MB=100`

---

### RAG Settings

#### `TOP_K_RESULTS`
- **Type:** Integer (1 - 100)
- **Default:** 5
- **Purpose:** Number of documents to retrieve per query
- **Trade-off:** More = better coverage, slower; Less = faster
- **Example:** `TOP_K_RESULTS=3`

#### `SIMILARITY_THRESHOLD`
- **Type:** Float (0.0 - 1.0)
- **Default:** 0.3
- **Purpose:** Minimum similarity score for document retrieval
- **Trade-off:** Higher = stricter, fewer results; Lower = more results
- **Example:** `SIMILARITY_THRESHOLD=0.5`

#### `RERANK_ENABLED`
- **Type:** Boolean
- **Default:** True
- **Purpose:** Re-rank retrieved documents (improves quality, adds latency)
- **Example:** `RERANK_ENABLED=false`

---

### Logging

#### `LOG_LEVEL`
- **Type:** String
- **Default:** `INFO`
- **Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Purpose:** Logging verbosity
- **Example:** `LOG_LEVEL=DEBUG`

#### `LOG_FILE`
- **Type:** Path
- **Default:** `./logs/mediscout.log`
- **Purpose:** Path to log file (directory created automatically)
- **Example:** `LOG_FILE=/var/log/mediscout.log`

---

## Common Configurations

### 🚀 **Performance Mode (Fast)**
```bash
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
CHUNK_SIZE=1500
TOP_K_RESULTS=3
SIMILARITY_THRESHOLD=0.4
LLM_TIMEOUT_SECONDS=10
```

### 🎯 **Quality Mode (Accurate)**
```bash
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct:free
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
CHUNK_SIZE=800
TOP_K_RESULTS=10
SIMILARITY_THRESHOLD=0.6
LLM_TIMEOUT_SECONDS=60
```

### 🐛 **Debug Mode**
```bash
LOG_LEVEL=DEBUG
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key_here
LANGCHAIN_PROJECT=mediscout-debug
```

### 💻 **Local-Only Mode (No External APIs except OpenRouter)**
```bash
LANGCHAIN_TRACING_V2=false
# Only local KB search, no PubMed (handled in UI)
```

---

## Validation

### Test Configuration Loading
```bash
python -c "from mediscout.config import get_settings; s = get_settings(); print(f'✓ Model: {s.openrouter_model}'); print(f'✓ PubMed: {s.pubmed_email}'); print(f'✓ LangSmith: {s.langsmith_enabled}')"
```

### Check Required Variables
```bash
python -c "from mediscout.config import get_settings; s = get_settings(); assert s.has_openrouter_key, 'Missing OpenRouter API key'; print('✓ All required variables set')"
```

---

## Troubleshooting

### ❌ `Configuration Error: 'Settings' object has no attribute 'openrouter_api_key'`

**Solution:** Check variable names in `.env` match this document exactly.

### ❌ LangSmith shows traces in "default" project

**Solution:** Use `LANGCHAIN_PROJECT` (not `LANGSMITH_PROJECT`):
```bash
LANGCHAIN_PROJECT=mediscout-dev
```

### ❌ `ValidationError: chunk_overlap must be less than chunk_size`

**Solution:** Ensure `CHUNK_OVERLAP < CHUNK_SIZE`:
```bash
CHUNK_SIZE=1000
CHUNK_OVERLAP=150  # Must be < 1000
```

### ❌ Environment variables not loading

**Solution:** Ensure `.env` file is in project root (same directory as `main.py`).

---

## Best Practices

1. **Never commit `.env` file** - It's in `.gitignore` for security
2. **Use `.env.example` as template** - Copy it to `.env` and fill in values
3. **Keep API keys secure** - Don't share or expose them
4. **Use LangSmith in development** - Helps debug LLM behavior
5. **Start with defaults** - Only change if you have performance issues
6. **Test after changes** - Run `python -c "from mediscout.config import get_settings; get_settings()"` to verify

---

## See Also

- [.env.example](.env.example) - Template configuration file
- [SETUP.md](SETUP.md) - Setup instructions for Anaconda users
- [SETUP-NON-ANACONDA.md](SETUP-NON-ANACONDA.md) - Setup for standard Python
- [src/mediscout/config.py](src/mediscout/config.py) - Configuration source code

