# Technical Design Document: MediScout - Multi-Agent AI Medical Researcher (MVP)

> Implementation-level design details for MediScout's MVP, covering all four agents, orchestration, data models, APIs, and deployment specifics.

---

## 1. Metadata

- **Project / System:** MediScout: Multi-Agent AI Medical Researcher
- **Component:** Complete MVP System (All Agents + Orchestrator + UI)
- **Author:** Python AI Developer (AI Persona) - Saro
- **Date:** 2025-11-08
- **Version:** 0.1.0-MVP
- **Technology Philosophy:** Open-source first, zero-cost LLMs via OpenRouter, local embeddings, ChromaDB for simplicity

---

## 2. Purpose & Scope

### Purpose
This document provides implementation-level technical guidance for building the MediScout MVP, covering:
- Python package structure and module organization
- Detailed API contracts for inter-agent communication
- Data models and storage mechanisms (ChromaDB, not FAISS)
- LLM integration via OpenRouter (free models: Llama 3.1, Gemma 2)
- Prompt templates optimized for open-source models
- Deployment configuration and environment setup

### Scope
- **In Scope:** All four agents (Retriever, Analysis, Insight, Report Builder), orchestrator, Streamlit UI, ChromaDB vector store, medical API clients, OpenRouter integration
- **Out of Scope:** Production infrastructure (Kubernetes, CI/CD), advanced monitoring, user authentication, multi-tenancy, paid LLM APIs

### Implementation Rationale & Thought Process

**Why This Design:**
1. **ChromaDB over FAISS:** Simpler persistence, metadata filtering, better DX for MVP
2. **OpenRouter:** Single API for free models (Llama 3.1 70B, Gemma 2 9B), no credit card needed
3. **Local Embeddings:** sentence-transformers (all-MiniLM-L6-v2) = $0 cost, privacy, fast
4. **Streamlit UI:** 50 lines vs 500 lines (React), perfect for hackathon demos
5. **Python 3.13:** Latest features, faster performance, sets up for future

---

## 3. Implementation Overview

### Architecture Component Mapping

| Architecture Component | Python Module | Primary Classes/Functions |
|------------------------|---------------|---------------------------|
| **Streamlit UI** | `src/ui/app.py` | `main()`, `setup_section()`, `research_section()` |
| **Agent Orchestrator** | `src/orchestrator/coordinator.py` | `AgentOrchestrator`, `WorkflowEngine` |
| **Contextual Retriever Agent** | `src/agents/retriever.py` | `RetrieverAgent`, `MultiSourceRetrieval` |
| **Critical Analysis Agent** | `src/agents/analysis.py` | `AnalysisAgent`, `StudyExtractor` |
| **Insight Generation Agent** | `src/agents/insight.py` | `InsightAgent`, `HypothesisGenerator` |
| **Report Builder Agent** | `src/agents/report_builder.py` | `ReportBuilderAgent`, `CitationFormatter` |
| **Vector Store** | `src/storage/vector_store.py` | `FAISSVectorStore`, `EmbeddingService` |
| **Medical API Clients** | `src/clients/` | `PubMedClient`, `ClinicalTrialsClient`, `ScholarClient` |
| **Domain Models** | `src/models/` | `Document`, `AnalysisResult`, `Hypothesis`, `Report` |

### Project Structure

```
mediscout/
├── pyproject.toml              # Dependencies & project config
├── README.md                   # Setup instructions
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore patterns
│
├── src/
│   ├── __init__.py
│   ├── config.py               # Configuration management
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   └── app.py              # Streamlit application
│   │
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── coordinator.py      # Main orchestrator
│   │   └── state_manager.py   # Session state management
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py             # Base agent interface
│   │   ├── retriever.py        # Contextual Retriever Agent
│   │   ├── analysis.py         # Critical Analysis Agent
│   │   ├── insight.py          # Insight Generation Agent
│   │   └── report_builder.py  # Report Builder Agent
│   │
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── pubmed.py           # PubMed API client
│   │   ├── clinical_trials.py # ClinicalTrials.gov client
│   │   └── scholar.py          # Google Scholar client
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   └── vector_store.py     # FAISS vector store
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── domain.py           # Domain entities
│   │   └── schemas.py          # Pydantic schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embedding.py        # Embedding generation
│   │   ├── text_extraction.py # PDF/TXT extraction
│   │   └── llm_service.py      # LLM API wrapper
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logging_config.py   # Logging setup
│       └── exceptions.py       # Custom exceptions
│
├── tests/
│   ├── __init__.py
│   ├── test_agents/
│   ├── test_clients/
│   └── test_orchestrator/
│
├── data/
│   ├── vector_stores/          # Persisted FAISS indexes
│   ├── uploads/                # Temporary file uploads
│   └── reports/                # Generated reports
│
└── docs/
    └── examples/               # Sample documents & queries
```

---

## 4. API Contracts & Schemas

### 4.1 Base Agent Interface

All agents implement this interface for consistent orchestration:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict
from src.models.domain import AgentResult

class BaseAgent(ABC):
    """Base interface for all MediScout agents."""
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute agent's primary function.
        
        Args:
            context: Execution context containing inputs and state
            
        Returns:
            AgentResult with outputs and metadata
        """
        pass
    
    @abstractmethod
    def validate_inputs(self, context: Dict[str, Any]) -> bool:
        """Validate required inputs are present."""
        pass
    
    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Return agent identifier."""
        pass
```

### 4.2 Pydantic Data Models

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum

# Enums
class DocumentSource(str, Enum):
    USER_UPLOAD = "user"
    PUBMED = "pubmed"
    CLINICAL_TRIALS = "clinicaltrials"
    GOOGLE_SCHOLAR = "scholar"

class StudyDesign(str, Enum):
    RCT = "randomized_controlled_trial"
    OBSERVATIONAL = "observational"
    CASE_STUDY = "case_study"
    META_ANALYSIS = "meta_analysis"
    SYSTEMATIC_REVIEW = "systematic_review"
    LABORATORY = "laboratory"
    UNKNOWN = "unknown"

class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Core Models
class Document(BaseModel):
    """Represents a research document."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    document_id: str = Field(..., description="Unique identifier")
    source: DocumentSource
    title: str
    authors: List[str] = Field(default_factory=list)
    abstract: str = ""
    content: str
    publication_date: Optional[str] = None
    url: Optional[str] = None
    doi: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=datetime.now)

class DocumentChunk(BaseModel):
    """Represents a text chunk for embedding."""
    chunk_id: str
    document_id: str
    content: str
    start_position: int
    end_position: int
    token_count: int
    embedding: Optional[List[float]] = None
    sequence_number: int

class RankedDocument(BaseModel):
    """Document with relevance scoring."""
    document: Document
    rank: int
    relevance_score: float
    ranking_method: str = "cosine_similarity"
    matched_chunks: List[str] = Field(default_factory=list)

class RetrievalResult(BaseModel):
    """Output from Contextual Retriever Agent."""
    retrieval_id: str
    query: str
    results: List[RankedDocument]
    source_breakdown: Dict[str, int]
    total_results: int
    retrieval_time_ms: int
    created_at: datetime = Field(default_factory=datetime.now)

class AnalysisResult(BaseModel):
    """Output from Critical Analysis Agent."""
    analysis_id: str
    document_id: str
    summary: str
    study_design: Optional[StudyDesign] = None
    population: Optional[str] = None
    intervention: Optional[str] = None
    outcomes: List[str] = Field(default_factory=list)
    statistical_significance: Optional[bool] = None
    reliability_score: float = Field(ge=0.0, le=1.0)
    contradictions: List[str] = Field(default_factory=list)
    key_quotes: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

class Hypothesis(BaseModel):
    """Generated hypothesis from Insight Agent."""
    hypothesis_id: str
    statement: str
    reasoning_chain: List[str]
    supporting_evidence: List[str]  # document IDs
    confidence_level: ConfidenceLevel
    research_gap: Optional[str] = None
    testability: str
    novelty_score: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)

class Report(BaseModel):
    """Final research report."""
    report_id: str
    title: str
    executive_summary: str
    research_topic: str
    methods_section: str
    detailed_findings: str
    contradictions_section: str
    hypotheses: List[Hypothesis]
    citations: List[str]
    metadata: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)

class AgentResult(BaseModel):
    """Generic agent execution result."""
    agent_name: str
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time_ms: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### 4.3 Agent-Specific Contracts

#### Retriever Agent Input/Output

```python
# Input Context
{
    "research_topic": str,
    "knowledge_base_id": str,
    "max_results": int = 20,
    "sources": List[str] = ["user", "pubmed", "clinicaltrials", "scholar"]
}

# Output
AgentResult(
    agent_name="retriever",
    success=True,
    data=RetrievalResult(...),
    execution_time_ms=2500
)
```

#### Analysis Agent Input/Output

```python
# Input Context
{
    "documents": List[Document],
    "research_topic": str,
    "batch_size": int = 5
}

# Output
AgentResult(
    agent_name="analysis",
    success=True,
    data=List[AnalysisResult],
    execution_time_ms=45000
)
```

#### Insight Agent Input/Output

```python
# Input Context
{
    "analyses": List[AnalysisResult],
    "research_topic": str,
    "max_hypotheses": int = 3
}

# Output
AgentResult(
    agent_name="insight",
    success=True,
    data=List[Hypothesis],
    execution_time_ms=15000
)
```

#### Report Builder Input/Output

```python
# Input Context
{
    "research_topic": str,
    "retrieval_result": RetrievalResult,
    "analyses": List[AnalysisResult],
    "hypotheses": List[Hypothesis],
    "citation_style": str = "AMA"
}

# Output
AgentResult(
    agent_name="report_builder",
    success=True,
    data=Report(...),
    execution_time_ms=8000
)
```

---

## 5. Data Models & Storage

### 5.1 Vector Store Schema (ChromaDB)

**Rationale for ChromaDB:**
- **Why:** Built-in persistence (SQLite), metadata filtering, simpler API, no separate metadata files
- **Thought Process:** FAISS is faster but requires manual metadata management. ChromaDB handles everything, reducing code by ~200 lines
- **Trade-off:** 10-20% slower queries, but for MVP with <10K documents, difference is negligible (<50ms)

```python
class ChromaDBVectorStore:
    """
    ChromaDB-backed vector store for document embeddings.
    
    Storage Structure:
    - Backend: SQLite database in data/chromadb/
    - Collections: One collection per knowledge base (isolated namespaces)
    - Embedding Dimension: 384 (all-MiniLM-L6-v2)
    - Metadata: Stored alongside vectors (no separate files)
    - Distance Metric: Cosine similarity (default)
    
    Advantages over FAISS:
    - Built-in persistence (no save/load methods needed)
    - Metadata filtering (e.g., filter by source="pubmed")
    - Automatic ID management
    - Update/delete individual documents
    """
    
    def __init__(self, knowledge_base_id: str, persist_directory: str = "./data/chromadb"):
        import chromadb
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=knowledge_base_id,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        self.kb_id = knowledge_base_id
    
    def add_documents(self, documents: List[Document], embeddings: List[List[float]]) -> None:
        """
        Add documents with embeddings to collection.
        
        Args:
            documents: List of Document objects
            embeddings: Pre-computed embeddings (384-dim each)
        """
        ids = [doc.document_id for doc in documents]
        metadatas = [
            {
                "source": doc.source,
                "title": doc.title,
                "url": doc.url or "",
                "publication_date": doc.publication_date or "",
            }
            for doc in documents
        ]
        documents_text = [doc.content[:1000] for doc in documents]  # Store excerpt
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents_text
        )
    
    def search(
        self, 
        query_embedding: List[float], 
        k: int = 10,
        filter: Optional[Dict[str, str]] = None
    ) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query vector (384-dim)
            k: Number of results
            filter: Optional metadata filter (e.g., {"source": "pubmed"})
        
        Returns:
            List of results with ids, distances, metadata
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter  # e.g., {"source": "pubmed"}
        )
        return results
    
    def update_document(self, document_id: str, embedding: List[float], metadata: Dict) -> None:
        """Update existing document (not possible with FAISS without rebuild)."""
        self.collection.update(
            ids=[document_id],
            embeddings=[embedding],
            metadatas=[metadata]
        )
    
    def delete_document(self, document_id: str) -> None:
        """Delete document by ID."""
        self.collection.delete(ids=[document_id])
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics."""
        return {
            "name": self.collection.name,
            "count": self.collection.count(),
            "metadata": self.collection.metadata
        }
```

**Why 384-dim instead of 768-dim:**
- all-MiniLM-L6-v2 produces 384-dim embeddings (not 768)
- Smaller dimension = faster queries, less storage (50% reduction)
- Quality still excellent for semantic search (Hugging Face benchmarks: 0.82 on STS)

### 5.2 Session State (Streamlit)

```python
# Stored in st.session_state
{
    "knowledge_base_id": str,
    "indexed_files": List[str],
    "current_status": str,
    "retrieval_result": Optional[RetrievalResult],
    "analyses": Optional[List[AnalysisResult]],
    "hypotheses": Optional[List[Hypothesis]],
    "final_report": Optional[Report],
    "error_message": Optional[str]
}
```

### 5.3 File System Storage

```
data/
├── vector_stores/
│   ├── {kb_id}.faiss          # FAISS index file
│   ├── {kb_id}.pkl            # Metadata pickle
│   └── {kb_id}_config.json    # KB configuration
│
├── uploads/                    # Temporary uploads (cleared after indexing)
│   └── {session_id}/
│       ├── document1.pdf
│       └── document2.txt
│
└── reports/                    # Generated reports
    └── {session_id}/
        └── research_report_{timestamp}.md
```

---

## 6. Service Design & Components

### 6.1 Embedding Service

```python
class EmbeddingService:
    """
    Generates embeddings using sentence-transformers or OpenAI.
    
    Model: sentence-transformers/all-MiniLM-L6-v2 (768-dim)
    Fallback: OpenAI text-embedding-3-small (1536-dim, truncated to 768)
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = 768
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        return self.model.encode(text).tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts."""
        return self.model.encode(texts, batch_size=32).tolist()
```

### 6.2 Text Extraction Service

```python
class TextExtractionService:
    """Extract text from various file formats."""
    
    def extract_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF using pypdf.
        
        Library: pypdf (lightweight, pure Python)
        Fallback: pdfminer.six for complex PDFs
        """
        pass
    
    def extract_from_txt(self, file_path: str) -> str:
        """Read plain text file."""
        pass
    
    def extract_from_csv(self, file_path: str) -> str:
        """Convert CSV to text representation."""
        pass
    
    def chunk_text(self, text: str, chunk_size: int = 500, 
                   overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Uses tiktoken for accurate token counting.
        """
        pass
```

### 6.3 Medical API Clients

#### PubMed Client

```python
class PubMedClient:
    """
    Client for NCBI E-utilities API (PubMed).
    
    API: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
    Rate Limit: 3 req/sec (no key), 10 req/sec (with key)
    """
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.rate_limiter = RateLimiter(max_calls=3 if not api_key else 10, period=1)
    
    async def search(self, query: str, max_results: int = 10) -> List[Document]:
        """
        Search PubMed and return documents.
        
        Process:
        1. ESearch: Get PMIDs for query
        2. EFetch: Fetch full records for PMIDs
        3. Parse XML to Document objects
        """
        pass
    
    def _parse_pubmed_article(self, xml_element) -> Document:
        """Parse PubMed XML to Document."""
        pass
```

#### ClinicalTrials.gov Client

```python
class ClinicalTrialsClient:
    """
    Client for ClinicalTrials.gov API v2.
    
    API: https://clinicaltrials.gov/api/v2/studies
    Rate Limit: Conservative 1 req/sec (undocumented)
    """
    
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
    
    async def search(self, query: str, max_results: int = 10) -> List[Document]:
        """
        Search clinical trials.
        
        Returns studies with status, phase, outcomes.
        """
        pass
```

#### Google Scholar Client

```python
class GoogleScholarClient:
    """
    Client for Google Scholar via SerpAPI.
    
    API: https://serpapi.com/google-scholar-api
    Rate Limit: 100 searches/month (free), 5000/month (paid)
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.serpapi_client = serpapi.Client(api_key)
    
    async def search(self, query: str, max_results: int = 10) -> List[Document]:
        """Search Google Scholar for academic papers."""
        pass
```

---

## 7. Model Integration & Invocation

### 7.1 LLM Service Wrapper (OpenRouter)

**Rationale for OpenRouter:**
- **Why:** Unified API for 100+ models, free options available, no credit card for Llama/Gemma
- **Thought Process:** Hackathon constraint = $0 budget. OpenRouter provides production-quality free models (Llama 3.1 70B, Gemma 2 9B)
- **Trade-offs:** Slight latency overhead (~200ms) vs direct API, but worth it for cost savings and flexibility

```python
class LLMService:
    """
    OpenRouter-based LLM client for access to multiple free models.
    
    Free Models Available:
    - meta-llama/llama-3.1-70b-instruct:free (Primary)
    - google/gemma-2-9b-it:free (Fallback)
    - mistralai/mistral-large:free (Alternative)
    
    Cost: $0 for free models (rate limited but generous)
    API: OpenAI-compatible interface
    """
    
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # Model selection rationale:
    # - Llama 3.1 70B: Best reasoning, 128K context, strong medical knowledge
    # - Gemma 2 9B: Fast, efficient, good for simple summaries
    # - Mistral Large: Alternative if others unavailable
    
    def __init__(
        self, 
        model: str = "meta-llama/llama-3.1-70b-instruct:free",
        api_key: str = None  # Optional, some models work without key
    ):
        import openai
        self.model = model
        self.client = openai.OpenAI(
            base_url=self.OPENROUTER_BASE_URL,
            api_key=api_key or os.getenv("OPENROUTER_API_KEY", "not-needed-for-free-models")
        )
    
    async def generate(
        self, 
        prompt: str, 
        system: str = None, 
        max_tokens: int = 4000, 
        temperature: float = 0.3
    ) -> str:
        """
        Generate completion using OpenRouter.
        
        Why these parameters:
        - temperature=0.3: Balance between creativity and consistency (medical domain needs accuracy)
        - max_tokens=4000: Sufficient for analysis outputs, avoid hitting limits
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            # OpenRouter-specific headers (optional)
            extra_headers={
                "HTTP-Referer": "https://github.com/mediscout",  # For ranking
                "X-Title": "MediScout Medical Research Assistant"
            }
        )
        return response.choices[0].message.content
    
    async def generate_structured(
        self, 
        prompt: str, 
        response_model: Type[BaseModel],
        system: str = None
    ) -> BaseModel:
        """
        Generate structured output using instructor library.
        
        Instructor wraps OpenRouter API to ensure JSON schema compliance.
        """
        import instructor
        client = instructor.from_openai(self.client)
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        return await client.chat.completions.create(
            model=self.model,
            response_model=response_model,
            messages=messages,
            max_tokens=4000,
            temperature=0.3
        )
    
    def switch_model(self, model: str) -> None:
        """
        Switch to different model (e.g., from 70B to 9B for speed).
        
        Use cases:
        - Use Llama 70B for complex hypothesis generation
        - Use Gemma 9B for simple document summaries
        """
        self.model = model
```

**Free Model Comparison:**

| Model | Size | Context | Speed | Quality | Best For |
|-------|------|---------|-------|---------|----------|
| **Llama 3.1 70B** | 70B params | 128K tokens | Medium | High | Hypothesis generation, complex reasoning |
| **Gemma 2 9B** | 9B params | 8K tokens | Fast | Good | Document summaries, simple tasks |
| **Mistral Large** | ~70B params | 128K tokens | Medium | High | Alternative to Llama, strong on structured output |

**Thought Process:**
- Start with Llama 3.1 70B for all tasks (highest quality)
- If rate limited, fallback to Gemma 2 9B (faster, still good)
- If both fail, try Mistral Large
- All models work without API key (rate limited but sufficient for hackathon)

### 7.2 Prompt Templates

#### Analysis Agent Prompt

```python
ANALYSIS_PROMPT_TEMPLATE = """
You are a medical research analyst. Analyze the following research document and provide a critical summary.

Research Topic: {research_topic}

Document:
Title: {title}
Authors: {authors}
Abstract: {abstract}

Instructions:
1. Summarize the key findings in 200-300 words
2. Identify the study design (RCT, observational, case study, etc.)
3. Extract: population, intervention, primary outcomes, statistical significance
4. Rate source reliability (0.0-1.0) based on study design and rigor
5. Note any limitations or potential contradictions

Return your analysis as structured JSON matching this schema:
{{
    "summary": "...",
    "study_design": "...",
    "population": "...",
    "intervention": "...",
    "outcomes": ["...", "..."],
    "statistical_significance": true/false,
    "reliability_score": 0.0-1.0,
    "key_quotes": ["...", "..."]
}}
"""
```

#### Insight Generation Prompt

```python
INSIGHT_PROMPT_TEMPLATE = """
You are a medical research scientist specializing in hypothesis generation.

Research Topic: {research_topic}

You have analyzed {num_documents} research documents. Here are the key findings:

{summarized_analyses}

Task: Generate 1-3 novel, testable hypotheses by synthesizing evidence across these documents.

For each hypothesis:
1. State the hypothesis clearly (1-2 sentences)
2. Provide a step-by-step reasoning chain (2-5 steps)
3. List supporting document IDs
4. Assess confidence level (low/medium/high)
5. Explain how it could be tested
6. Rate novelty (0.0-1.0)

Focus on:
- Cross-domain connections
- Unexpected correlations
- Mechanism proposals
- Drug repurposing opportunities

Return structured JSON:
{{
    "hypotheses": [
        {{
            "statement": "...",
            "reasoning_chain": ["Step 1: ...", "Step 2: ..."],
            "supporting_evidence": ["doc_id_1", "doc_id_2"],
            "confidence_level": "medium",
            "testability": "...",
            "novelty_score": 0.7
        }}
    ]
}}
"""
```

### 7.3 Token Management

```python
class TokenManager:
    """Track and limit LLM token usage."""
    
    MAX_TOKENS_PER_SESSION = 100000  # Prevent runaway costs
    
    def __init__(self):
        self.session_usage = {"prompt_tokens": 0, "completion_tokens": 0}
    
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens using tiktoken."""
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    
    def check_limit(self) -> bool:
        """Check if session is under token limit."""
        total = self.session_usage["prompt_tokens"] + self.session_usage["completion_tokens"]
        return total < self.MAX_TOKENS_PER_SESSION
```

---

## 8. Infra, Deployment & IaC

### 8.1 Runtime Environment

**Development:**
```bash
# Python 3.13+ with uv package manager
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e ".[dev]"
```

**Dependencies (pyproject.toml):**

**Rationale for Dependencies:**
- **ChromaDB** replaces faiss-cpu (simpler API, built-in persistence)
- **OpenAI SDK** used for OpenRouter (OpenAI-compatible API)
- **No anthropic** package needed (OpenRouter handles all models)
- **instructor** added for structured LLM outputs (type-safe JSON generation)
- **loguru** replaces stdlib logging (better DX)
- **tenacity** for retry logic (exponential backoff for APIs)

```toml
[project]
name = "mediscout"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    # UI & Framework
    "streamlit>=1.28.0",          # Apache 2.0 - Web UI
    
    # Agent Orchestration
    "langgraph>=0.2.0",           # MIT - Agent workflow engine
    "langchain>=0.3.0",           # MIT - LLM framework
    "langchain-community>=0.3.0", # MIT - Community integrations
    "langsmith>=0.1.0",           # Proprietary (Free tier) - Observability (optional but recommended)
    
    # LLM & Embeddings
    "openai>=1.0.0",              # Apache 2.0 - OpenRouter uses OpenAI SDK
    "instructor>=0.4.0",          # MIT - Structured LLM outputs
    "sentence-transformers>=2.2.0", # Apache 2.0 - Local embeddings
    "transformers>=4.35.0",       # Apache 2.0 - Model loading
    "torch>=2.1.0",               # BSD-3 - ML backend (CPU-only sufficient)
    
    # Vector Database
    "chromadb>=0.4.0",            # Apache 2.0 - Vector store (replaces FAISS)
    
    # Data Validation
    "pydantic>=2.0.0",            # MIT - Type-safe data models
    
    # Document Processing
    "pypdf>=3.17.0",              # BSD-3 - PDF extraction
    "pdfminer.six>=20221105",     # MIT - Fallback PDF parser
    "pandas>=2.1.0",              # BSD-3 - CSV handling
    
    # HTTP & APIs
    "httpx>=0.25.0",              # BSD-3 - Async HTTP client
    "biopython>=1.81",            # BSD-3 - PubMed API
    "serpapi>=0.1.0",             # MIT - Google Scholar
    
    # Utilities
    "tiktoken>=0.5.0",            # MIT - Token counting
    "python-dotenv>=1.0.0",       # BSD-3 - .env file support
    "tenacity>=8.2.0",            # Apache 2.0 - Retry logic
    "loguru>=0.7.0",              # MIT - Better logging
    "pyyaml>=6.0",                # MIT - Config files
]

[project.optional-dependencies]
dev = [
    # Testing
    "pytest>=7.4.0",              # MIT - Test framework
    "pytest-asyncio>=0.21.0",     # Apache 2.0 - Async tests
    "pytest-mock>=3.12.0",        # MIT - Mocking
    
    # Code Quality
    "black>=23.9.0",              # MIT - Code formatter
    "ruff>=0.1.0",                # MIT - Fast linter
    "mypy>=1.7.0",                # MIT - Type checker
    
    # Security
    "bandit>=1.7.0",              # Apache 2.0 - Security linter
    "safety>=2.3.0",              # MIT - Vulnerability scanner
]

[project.urls]
Homepage = "https://github.com/your-org/mediscout"
Documentation = "https://github.com/your-org/mediscout/docs"
Repository = "https://github.com/your-org/mediscout"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Total Dependencies:**
- **Core:** 21 packages (20 required + 1 optional LangSmith)
- **Dev:** 9 packages
- **Total Install Size:** ~2.5 GB (torch is largest at ~800MB)
- **Licenses:** All permissive (MIT, Apache 2.0, BSD-3) + LangSmith (free tier available)

**Why torch (large dependency):**
- Required by sentence-transformers for embedding generation
- CPU-only version sufficient (no GPU needed)
- Alternative: Use OpenAI embeddings API (adds cost, removes privacy benefit)

### 8.2 Environment Configuration

**.env.example:**

**Rationale for Environment Variables:**
- **OPENROUTER_API_KEY:** Optional for free models (Llama 3.1, Gemma 2 work without it)
- **PUBMED_API_KEY:** Optional but recommended (increases rate limit from 3 to 10 req/sec)
- **SERPAPI_KEY:** Required only if using Google Scholar (100 searches/month free tier)

```bash
# LLM Provider (OpenRouter)
OPENROUTER_API_KEY=optional  # Not needed for free models (Llama 3.1, Gemma 2)
DEFAULT_LLM_MODEL=meta-llama/llama-3.1-70b-instruct:free
FALLBACK_LLM_MODEL=google/gemma-2-9b-it:free

# Medical APIs
PUBMED_API_KEY=your_key_here  # Optional, increases rate limit from 3 to 10 req/sec
SERPAPI_KEY=your_key_here     # Required for Google Scholar ($0.05/search or 100 free/month)

# Configuration
DEFAULT_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # Local, no API key needed
MAX_DOCUMENTS_PER_QUERY=20
CHUNK_SIZE=500                # Tokens per chunk
CHUNK_OVERLAP=100             # Token overlap between chunks
VECTOR_STORE_PATH=./data/chromadb     # ChromaDB storage
REPORTS_PATH=./data/reports

# Performance
MAX_CONCURRENT_API_REQUESTS=3  # Avoid rate limits
LLM_REQUEST_TIMEOUT=60         # Seconds
EMBEDDING_BATCH_SIZE=32        # Process embeddings in batches

# Logging
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR
LOG_FILE=./logs/mediscout.log

# LangSmith (Observability - Optional but Recommended)
LANGCHAIN_TRACING_V2=true          # Enable LangSmith tracing
LANGCHAIN_API_KEY=your_key_here    # Free tier: 5K traces/month
LANGCHAIN_PROJECT=mediscout-mvp    # Project name in LangSmith dashboard

# Feature Flags (for gradual rollout)
ENABLE_GOOGLE_SCHOLAR=true   # Set false to disable Scholar (save API costs)
ENABLE_CLINICAL_TRIALS=true
ENABLE_HYPOTHESIS_GENERATION=true
```

**Minimal Setup (Zero Cost):**
```bash
# No API keys needed! Just run with defaults
# - OpenRouter free models work without key
# - Local embeddings (no API)
# - PubMed works without key (lower rate limit)
# - Skip Google Scholar to avoid SerpAPI cost
DEFAULT_LLM_MODEL=meta-llama/llama-3.1-70b-instruct:free
DEFAULT_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
ENABLE_GOOGLE_SCHOLAR=false
LOG_LEVEL=INFO
```

### 8.3 Deployment (MVP)

**Local Development:**
```bash
# Run Streamlit app
streamlit run src/ui/app.py --server.port 8501
```

**Docker (Future):**
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . /app

RUN pip install uv && uv pip install -e .

EXPOSE 8501
CMD ["streamlit", "run", "src/ui/app.py"]
```

---

## 9. Observability & Testing

### 9.1 Logging Strategy

```python
# logging_config.py
import logging
import sys

def setup_logging(level: str = "INFO"):
    """Configure structured logging."""
    logging.basicConfig(
        level=getattr(logging, level),
        format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/mediscout.log")
        ]
    )
```

**Key Metrics to Log:**
- API call durations and success rates
- LLM token usage per agent
- Document processing times
- Retrieval precision metrics
- Hypothesis generation count and confidence distribution

### 9.2 Testing Strategy

**Unit Tests:**
```python
# tests/test_agents/test_retriever.py
import pytest
from src.agents.retriever import RetrieverAgent

@pytest.mark.asyncio
async def test_retriever_local_search():
    """Test vector store querying."""
    agent = RetrieverAgent()
    context = {"research_topic": "GIST prevention", "knowledge_base_id": "test_kb"}
    result = await agent.execute(context)
    
    assert result.success
    assert len(result.data.results) > 0
    assert result.data.results[0].relevance_score > 0.4
```

**Integration Tests:**
```python
# tests/test_orchestrator/test_workflow.py
@pytest.mark.asyncio
async def test_end_to_end_workflow():
    """Test full research workflow."""
    orchestrator = AgentOrchestrator()
    result = await orchestrator.run_research_workflow(
        topic="COVID-19 vaccine efficacy",
        knowledge_base_id="test_kb"
    )
    
    assert result["report"] is not None
    assert len(result["hypotheses"]) >= 1
```

**Test Fixtures:**
```python
# tests/conftest.py
@pytest.fixture
def sample_documents():
    """Provide sample medical documents for testing."""
    return [
        Document(
            document_id="doc_1",
            source=DocumentSource.PUBMED,
            title="Sample RCT Study",
            content="...",
        )
    ]
```

---

## 10. Security & Compliance

### 10.1 Authentication & Authorization
- **MVP:** No authentication (local single-user app)
- **Future:** Implement OAuth 2.0 with role-based access

### 10.2 Data Handling
- **User Documents:** Stored locally, never sent to cloud without encryption
- **API Keys:** Stored in `.env`, never committed to Git
- **LLM Prompts:** Sanitize inputs to prevent prompt injection

### 10.3 Error Handling

```python
class MediScoutException(Exception):
    """Base exception for MediScout errors."""
    pass

class APIRateLimitError(MediScoutException):
    """External API rate limit exceeded."""
    pass

class LLMGenerationError(MediScoutException):
    """LLM generation failed."""
    pass

class VectorStoreError(MediScoutException):
    """Vector store operation failed."""
    pass
```

---

## 11. Operational Runbook (Summary)

### Start Application
```bash
cd mediscout
source .venv/bin/activate
streamlit run src/ui/app.py
```

### Clear Vector Store
```bash
rm -rf data/vector_stores/*
```

### Reset Session
- Refresh Streamlit page or use "Clear Cache" button

### Common Issues

**Issue: PubMed API Rate Limit**
- Symptom: HTTP 429 errors in logs
- Action: Add API key to `.env`, reduce concurrent requests

**Issue: Vector Store Not Found**
- Symptom: "Knowledge base not found" error
- Action: Re-index documents in Setup section

**Issue: LLM Timeout**
- Symptom: Request exceeds 60 seconds
- Action: Reduce batch size, use faster model (GPT-4o-mini)

---

## 12. Performance & Cost Considerations

### Expected Performance
- **Document Indexing:** 10 PDFs in ~30 seconds
- **Retrieval:** < 500ms for vector search, 2-3s for API queries
- **Analysis:** ~10s per document (LLM-dependent)
- **Full Workflow:** < 2 minutes for 20 documents

### Cost Estimates (Per Research Query)

**With Our Zero-Cost Stack:**

| Component | Usage | Cost (USD) | Rationale |
|-----------|-------|------------|-----------|
| Embedding (local) | 50K tokens | **$0** | sentence-transformers runs locally |
| LLM Analysis (OpenRouter Llama 3.1 Free) | 100K input, 20K output | **$0** | Free tier, rate limited but sufficient |
| PubMed API | 10 queries | **$0** | Free public API |
| ClinicalTrials API | 5 queries | **$0** | Free public API |
| Google Scholar (SerpAPI) | 1 query | $0.05 or $0 | Optional, disable to save cost |
| **Total per Query** | | **$0 - $0.05** | Nearly free! |

**Cost Comparison (If We Used Paid APIs):**

| Component | Paid Option | Our Choice | Savings per Query |
|-----------|-------------|------------|-------------------|
| Embeddings | OpenAI ($0.00025) | Local (free) | $0.00025 |
| LLM | GPT-4 ($0.36) | Llama 3.1 Free ($0) | $0.36 |
| Vector DB | Pinecone ($0.10) | ChromaDB (free) | $0.10 |
| **Total Savings** | | | **$0.46 per query** |

**For 100 Queries (hackathon demo):**
- **Our Cost:** $0 - $5 (if using Google Scholar)
- **Traditional Stack Cost:** $46+
- **Savings:** 90-100%

**Optimization Strategies:**
- ✅ Local embeddings (implemented) - Saves $0.00025/query
- ✅ OpenRouter free models (implemented) - Saves $0.36/query
- ✅ Cache API responses (5-min TTL) - Reduces PubMed calls by ~50%
- ✅ ChromaDB local storage (implemented) - Saves $0.10/query
- ⚙️ Disable Google Scholar for demo (optional) - Saves $0.05/query
- ⚙️ Batch document processing - Reduces redundant work

**Thought Process:**
- **Goal:** Zero-cost hackathon demo
- **Challenge:** Traditional stack (OpenAI + Pinecone) = $0.50/query = $50 for 100 demos
- **Solution:** Free alternatives with minimal quality trade-off
- **Result:** Llama 3.1 70B rivals GPT-4 on reasoning tasks, local embeddings ~95% quality of OpenAI

---

## 13. Migration / Backwards Compatibility

**MVP Considerations:**
- No migrations required (fresh system)
- Vector store format tied to embedding model version
- If model changes, full re-indexing required

**Future Schema Changes:**
- Version all data models (`version: str` field)
- Implement migration scripts in `src/migrations/`
- Maintain backward compatibility for 2 versions

---

## 14. Security Review & Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| API key leakage | High | Use `.env`, add to `.gitignore`, never log keys |
| Prompt injection | Medium | Sanitize user inputs, use system prompts |
| Excessive costs | Medium | Token limits, rate limiting, cost alerts |
| Data loss | Low | Persist vector stores, backup before re-indexing |

**Security Checklist:**
- [ ] `.env` in `.gitignore`
- [ ] Input validation on all user inputs
- [ ] HTTPS for all external API calls
- [ ] No PII in logs
- [ ] Medical disclaimer in UI and reports

---

## 15. Open Questions & Action Items

| ID | Question | Owner | Status |
|----|----------|-------|--------|
| Q1 | Use local embedding model or OpenAI API? | Dev Lead | **Decision: Local (cost optimization)** |
| Q2 | FAISS vs ChromaDB for vector store? | Dev Lead | **Decision: FAISS (simpler for MVP)** |
| Q3 | Should we cache API responses persistently? | Dev Team | Open |
| Q4 | What's the optimal chunk size for medical papers? | Data Scientist | Open (test with 500 tokens) |

**Action Items:**
- [ ] Set up development environment
- [ ] Implement base agent interface
- [ ] Create test fixtures with sample medical documents
- [ ] Benchmark embedding models (local vs API)
- [ ] Test PubMed API integration with rate limiting

---

## 16. References

- **Architecture Document:** `docs/project-docs/architecture-mvp.md`
- **Domain Model:** `docs/project-docs/domain-model.md`
- **PRD:** `docs/project-docs/prd.md`
- **AI Personas:** `docs/ai-personas/`
- **LangGraph Documentation:** https://langchain-ai.github.io/langgraph/
- **FAISS Documentation:** https://github.com/facebookresearch/faiss
- **PubMed E-utilities:** https://www.ncbi.nlm.nih.gov/books/NBK25501/

---

*This technical design document should be updated as implementation progresses. Version this document and track changes in Git.*

