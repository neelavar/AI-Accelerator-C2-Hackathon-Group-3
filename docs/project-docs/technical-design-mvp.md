# Technical Design Document (TDD) Template

---

## 1. Metadata
- **Project / System:** MediScout: Multi-agent AI Medical Researcher
- **Component:** MVP - Full System
- **Author:** AI Solution Architect
- **Date:** 2025-11-08
- **Version:** 0.1

## 2. Purpose & Scope
This Technical Design Document (TDD) provides implementation-level design details for the Minimum Viable Product (MVP) of the MediScout: Multi-agent AI Medical Researcher. It covers the core components, data flows, and integration points necessary to achieve the objectives outlined in the Product Requirements Document (PRD) and the AI Solution Architecture (MVP) document. This document intentionally excludes detailed UI/UX design, comprehensive error handling beyond the LangGraph state, and production-level deployment specifics.

## 3. Implementation Overview
The system is designed as a stateful, agentic workflow orchestrated by LangGraph. It integrates user-provided knowledge with external medical data sources to generate structured research reports.

**Mapping of Architecture Components to Code Modules:**
- **Streamlit UI:** `main.py`
- **Configuration Management:** `src/config.py`
- **Knowledge Base Management (Ingestion & Retrieval):** `src/knowledge_base.py`
- **Agent Orchestration (LangGraph):** `src/orchestrator.py`
- **Individual Agent Logic:** `src/agents/` (e.g., `retriever_agent.py`, `analysis_agent.py`, `insight_agent.py`, `report_agent.py`)
- **External API Clients:** `src/services/external_apis.py`
- **Persistent Data Storage:** `data/chromadb/`

## 4. API Contracts & Schemas
For the MVP, the primary "API contract" is the shared state object passed between nodes in the LangGraph workflow. This section details how agent outputs are structured and how the graph state is managed.

### 4.1. Structured Agent Outputs
To ensure predictable and reliable data flow between agents, we will enforce structured outputs from LLM calls using a **Pydantic and Tool-Calling** strategy.

1.  **Schema Definition:** The desired output for any agent is defined as a Pydantic `BaseModel`. This provides a clear, version-controlled, and type-safe schema.

    ```python
    # Example schema for the Critical Analysis Agent's output
    from pydantic import BaseModel, Field
    from typing import List, Optional
    
    class SourceAnalysis(BaseModel):
        source_id: str = Field(description="The unique identifier for the source document.")
        summary: str = Field(description="A concise summary of the source's key findings.")
        contradictions: Optional[List[str]] = Field(description="Any contradictions found when compared to other sources.")
    
    class CriticalAnalysisOutput(BaseModel):
        analyses: List[SourceAnalysis]
    ```

2.  **Tool-Calling Invocation:** Instead of parsing text, we will instruct the LLM to use a "tool" whose schema matches our Pydantic model. Modern LLMs can generate a conforming JSON object directly. LangChain's `.with_structured_output()` method will be used to automate this, including parsing, validation, and self-correction loops.

This approach ensures that the data placed into the graph state is always valid and correctly formatted.

### 4.2. Graph State Management
We will use an **"accumulator" pattern** for managing the `ResearchState` as it flows through the graph.

1.  **Central State Object:** The `ResearchState` `TypedDict` is the single source of truth.

    ```python
    # src/state.py (Conceptual)
    from typing import TypedDict, List, Optional
    
    # Using the Pydantic model for the 'analysis' field
    # from .agents.schemas import CriticalAnalysisOutput 
    
    class ResearchState(TypedDict):
        topic: str
        user_docs: List[str]
        web_results: List[str]
        analysis: Optional[dict] # Initially a dict, to be populated by a Pydantic model instance
        hypotheses: List[str]
        report: str
        error: Optional[str]
    ```

2.  **State Enrichment:** Each agent's role is to **add to** the state, not replace it. For example, the `RetrieverAgent` adds to the `web_results` list, and the `AnalysisAgent` populates the `analysis` field. This progressively enriches the state object at each step.

3.  **Conditional Routing:** The graph will use conditional edges to route the workflow based on the contents of the state. For example, a `Validate Retrieved Data` node will check if `state['web_results']` is empty and route to an error handler if it is, thus ensuring downstream agents always have the context they need.

**External API Interactions:**
- **PubMed, openFDA, ClinicalTrials.gov, Google Scholar:** Standard RESTful API calls. Request and response schemas will adhere to the respective API documentation. `httpx` will be used for asynchronous requests.

## 5. Data Models & Storage
- **Vector Store:** ChromaDB, running in-process and persisting to the local filesystem in the `data/chromadb/` directory.
    - Stores embeddings and original text content of user-provided documents.
    - **Indexing:** Documents (`.txt`, `.pdf`, `.csv`) are parsed, chunked, and embedded.
    - **Chunking Strategy:** To be determined (TBD) during implementation, focusing on maximizing retrieval relevance and minimizing token usage. Initial approach will be fixed-size chunks with overlap.

## 6. Service Design & Components
- **`main.py` (Streamlit UI):**
    - Entry point for the application.
    - Handles user input (research topic, file uploads).
    - Displays real-time status updates and the final report.
    - Triggers the LangGraph orchestration.
- **`src/config.py`:**
    - Manages environment variables (`.env`).
    - Configures LLM clients (OpenAI-compatible API for OpenRouter/Ollama) based on `APP_ENV` (DEV/DEMO).
    - Provides access to model names (`EMBEDDING_MODEL`, `FAST_MODEL`, `THINKING_MODEL`).
- **`src/knowledge_base.py`:**
    - **File Ingestion:** Uses `pypdf` for PDF parsing and `unstructured[local-inference]` for robust document parsing (TXT, CSV, etc.).
    - **Embedding Generation:** Interfaces with the configured embedding model (`llm_client.embeddings.create`).
    - **ChromaDB Management:** Initializes, updates, and queries the ChromaDB instance.
- **`src/orchestrator.py`:**
    - Defines the LangGraph `StateGraph` and its nodes (agents) and edges.
    - Manages the flow of the `ResearchState` object between agents.
    - Implements conditional routing based on agent outputs (e.g., `Validate Query`, `Validate Retrieved Data`).
- **`src/agents/*.py`:**
    - **`base_agent.py`:** Defines an abstract `BaseAgent` class from which all other agents inherit. It standardizes the agent interface (e.g., an `execute` method) and can contain shared logic for logging or LLM invocation.
    - Each file contains the logic for a major, complex agent node, inheriting from `BaseAgent`.
    - **`retriever_agent.py`:** Implements the logic for both parallel retrieval nodes. It should use the `FAST_MODEL` for any query transformations to optimize API calls.
        - **Node 2a: Knowledge Base Retriever:** Queries the local ChromaDB using a vector embedding of the user's topic.
        - **Node 2b: Web Researcher:** Transforms the user's topic into optimal search queries for external APIs (PubMed, etc.).
    - **`analysis_agent.py`:** Implements **Node 5: Critical Analysis Agent**.
    - **`insight_agent.py`:** Implements **Node 6: Insight Generation Agent**.
    - **`report_agent.py`:** Implements **Node 7: Report Builder Agent`**.
- **`src/services/external_apis.py`:**
    - Contains client implementations for PubMed, openFDA, ClinicalTrials.gov, and Google Scholar APIs.
    - Handles API key management, rate limiting, and basic retry logic.

## 7. Model Integration & Invocation
- **Hybrid Model Strategy:**
    - **Embedding Model:** `nomic-embed-text` (Ollama for DEV) / `nomic-ai/nomic-embed-text-v1.5` (OpenRouter for DEMO). Used for generating vector embeddings.
    - **Fast Models:** `mistral` (Ollama for DEV) / `mistralai/mistral-7b-instruct` (OpenRouter for DEMO). Used for summarization, data extraction, and formatting (e.g., `Validate Query` agent).
    - **Heavy Models:** `deepseek-r1:8b` (Ollama for DEV) / `openai/gpt-4o` (OpenRouter for DEMO). Used for complex reasoning tasks like critical analysis, contradiction detection, and hypothesis generation.
- **Configuration:** Model selection is now driven entirely by environment variables loaded from the `.env` file, as defined in `src/config.py`. This allows for flexible configuration without code changes. The following environment variables control the model setup: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_EMBEDDING_MODEL`, `LLM_FAST_MODEL`, and `LLM_THINKING_MODEL`.
- **Prompt Templates:** Each agent will utilize specific prompt templates, designed for its role, to guide LLM behavior and ensure structured outputs.
- **Context Handling:** The LangGraph state will manage the context passed to LLMs, ensuring relevant information is provided within token limits.
- **Fallback & Retry:** Basic retry mechanisms (e.g., using `tenacity` library) will be implemented for external API calls and potentially for LLM invocations.

## 8. Infra, Deployment & IaC
- **Runtime Environment:** Python 3.10+, `uv` for dependency management.
- **Deployment Topology (MVP):** Single-user, local execution. The Streamlit application runs as a single Python process.
- **Installation:**
    1.  Set up `.env` file (copy from `.env.example`).
    2.  Install dependencies: `uv pip install -e .`
    3.  Run the application: `streamlit run main.py`
- **Secrets & Config Management:** API keys and other sensitive configurations are loaded from the `.env` file via `python-dotenv` and managed by `src/config.py`.

## 9. Observability & Testing
- **Observability Tooling:** LangSmith will be used for comprehensive tracing and monitoring of agent execution, LLM calls, and state transitions.
    - Enabled via environment variables: `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`.
- **Testing Strategy (MVP):**
    - **Unit Tests:** For individual agent logic and utility functions.
    - **Integration Tests:** To verify the LangGraph workflow with mock LLM responses and external API calls.
    - **Manual Testing:** Via the Streamlit UI for end-to-end flow and report quality.

## 10. Security & Compliance
- **Data Privacy:** User-uploaded documents are stored locally in ChromaDB within the `data/chromadb/` directory. No user data is sent to external services unless explicitly part of an LLM prompt or external API query.
- **API Keys:** Stored in `.env` and accessed securely via environment variables.
- **Disclaimer:** The UI and generated reports will clearly state that the output is AI-generated for research assistance and requires human verification.

## 11. Operational Runbook (Summary)
- **Start Application:**
    1.  Ensure Python environment is set up and dependencies are installed (`uv pip install -e .`).
    2.  Ensure `.env` file is configured.
    3.  Run `streamlit run main.py` from the project root.
- **Troubleshooting:**
    - Check console logs for errors.
    - Verify `.env` configuration.
    - Check LangSmith traces for detailed execution flow and LLM issues.

## 12. Performance & Cost Considerations
- **Performance Target:** End-to-end report generation within 2 minutes for the demo.
- **Optimization:** Hybrid model strategy (fast models for simple tasks, heavy models for complex reasoning) to balance latency and cost.
- **Cost Drivers:** Primarily LLM API calls (especially heavy models) and external API usage.

## 13. Migration / Backwards Compatibility
- Not applicable for MVP v0.1.

## 14. Security Review & Risk Assessment
- **LLM Hallucination:** Mitigated by source linking, critical analysis agent, and clear disclaimers.
- **API Unreliability/Rate Limits:** Mitigated by retry logic in `external_apis.py`.
- **Data Privacy:** User data remains local.

## 15. Open Questions & Action Items
- **Q1:** Which specific small and large models offer the best performance/cost/latency trade-off? (e.g., Llama3-8B vs. Mistral-7B vs. Gemma-7B? Claude 3 Sonnet vs. Opus vs. GPT-4o?).
- **Q2:** What is the optimal chunking strategy for document ingestion to maximize retrieval relevance?
- **Action Item:** Develop a PoC of the LangGraph state machine with mock agent nodes.
- **Action Item:** Benchmark the latency and quality of at least two small and two large models for their designated tasks.
- **Action Item:** Implement the file ingestion and ChromaDB indexing pipeline.

## 16. References
- [Product Requirements Document (PRD): MediScout - Multi-Agent AI Medical Researcher](../../project-docs/prd.md)
- [AI Solution Architecture: Multi-agent AI Deep Researcher (MVP)](../../project-docs/architecture-mvp.md)
- [Project Structure & Setup Guide](../../project-docs/project-structure.md)
- [AI Solution Architect & Agentic Systems Designer Persona](../../ai-personas/40_solution-architect.md)
