# Scripts

This README explains how to run the small integration/test scripts in the `scripts/` and `src/` folders used for quick verification of the PubMed client, the KnowledgeBase (Chroma vector store) and the orchestrator workflow.

## Purpose

- Provide quick, reproducible checks that the external API client (PubMed), the local knowledge-base/vector store (Chroma) and the LangGraph-based orchestrator are working in your environment.

## Prerequisites

- Python 3.10+ (use pyenv or system Python). The project dependencies are declared in `requirements.txt` / `pyproject.toml`.
- A virtual environment is recommended:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Configuration / Environment variables

The project reads settings from environment variables or a `.env` file via `src/config.py` (Pydantic Settings). The README below shows common values to set. Create a `.env` in the repo root with at least the following (or export them in your shell):

```env
# LLM / embedding provider (defaults are development-friendly)
LLM_BASE_URL=http://localhost:11434
LLM_API_KEY=ollama
LLM_EMBEDDING_MODEL=nomic-embed-text

# ChromaDB / vector store
CHROMA_PERSIST_DIR=data/chromadb
CHROMA_COLLECTION_NAME=mediscout_kb

# Optional: If you later integrate a PubMed API key
# PUBMED_API_KEY=your_pubmed_api_key_here
```

Notes:
- `LLM_BASE_URL` and `LLM_API_KEY` should point to your local or remote embedding/LLM service. The default values assume a local dev setup.
- `CHROMA_PERSIST_DIR` must be writable by the user running the scripts.

## Running the verification scripts

1) PubMed client quick-check

- This script performs a small PubMed search and prints results. It uses the `PubMedClient` in `src/services/external_apis.py` and `src/config.py` for optional keys.

Run it directly:

```bash
python scripts/test_pubmed_client.py
```

Output: the script prints the search query and a small number of article metadata/content snippets.

2) KnowledgeBase (Chroma) basic test

- `src/knowledge_base.py` includes an example `main()` that demonstrates initializing embeddings, adding a simple text file, and running a similarity search. It will persist Chroma data to `CHROMA_PERSIST_DIR` as configured.

Run the example file directly (it creates a small temporary text file and cleans up):

```bash
python src/knowledge_base.py
```

If you already have documents to test, update the example calls or call the `KnowledgeBase` class from a short script. Remember to clear or inspect the `CHROMA_PERSIST_DIR` if you want clean runs.

3) Orchestrator / workflow test

- `scripts/test_orchestrator.py` initializes the LangGraph workflow defined in `src/orchestrator.py` and runs it with a mock initial state. This verifies the nodes and conditional edges are wired correctly (uses internal mocks for external clients).

Run it directly:

```bash
python scripts/test_orchestrator.py
```

You should see node-by-node outputs printed to the console.

4) Run the project's unit tests

- The repository contains further unit tests under `tests/` and some quick scripts under `scripts/`. To run all pytest tests:

```bash
python -m pytest -q
```

Or target a single script/test file, e.g.:

```bash
python -m pytest scripts/test_pubmed_client.py -q
```

## Troubleshooting

- Missing dependencies / import errors: ensure your virtualenv is active and `pip install -r requirements.txt` completed without errors.
- LLM / embeddings not available: If the embedding model or LLM endpoint at `LLM_BASE_URL` is not up the KnowledgeBase initialization may fail. Start your local LLM/embed server or set `LLM_BASE_URL` to a reachable host.
- Chroma errors: Check that `CHROMA_PERSIST_DIR` exists and is writable. Remove or clear the directory to reset state between runs.
- PubMed rate limits or network errors: If searches fail due to network or rate-limiting, try again or configure `PUBMED_API_KEY` if required by your integration.

---

Last updated: 2025-11-09

