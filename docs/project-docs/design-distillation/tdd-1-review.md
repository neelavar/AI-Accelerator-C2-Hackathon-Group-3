# Critical Review of Technical Design Document (tdd-1.md)

- **Author:** AI Solution Architect
- **Date:** 2025-11-09
- **Status:** **Rejected**. This document requires major revisions before it can be approved.

---

## 1. Executive Summary

This review assesses the Technical Design Document `tdd-1.md` authored by Saro. While the document shows detailed effort in defining schemas and exploring tooling, it is rejected due to **critical internal contradictions, significant deviations from the established solution architecture, and technical inaccuracies.**

The inconsistencies, particularly regarding the choice of vector store (FAISS vs. ChromaDB), undermine the document's reliability. Furthermore, the omission of key architectural components, such as the validation and guardrail agents, compromises the system's robustness and security, which were core tenets of the approved architecture (`architecture-mvp.md`).

This document cannot be used for implementation in its current state. The author must address the issues outlined below and resubmit for approval.

## 2. Critical Contradictions

A technical design must be a source of truth. The presence of numerous direct contradictions makes this document unusable.

| Contradiction ID | Issue | Evidence | Impact |
| :--- | :--- | :--- | :--- |
| **C-1** | **Vector Store Identity Crisis (FAISS vs. ChromaDB)** | The document repeatedly contradicts itself. **Rationale (Sec 2), Code (Sec 5.1), and Dependencies (Sec 8.1) state ChromaDB will be used.** However, the **Component Map (Sec 3), Project Structure (Sec 3), and File System Diagram (Sec 5.3) all explicitly reference FAISS.** This is compounded by **Open Question Q2 (Sec 15), which lists the decision as "FAISS (simpler for MVP)"**—directly opposing the rationale in Section 2. | **Critical.** The development team has no clear direction on a fundamental data component. This indicates a lack of attention to detail and review before submission. |
| **C-2** | **Incorrect Embedding Dimension** | **Section 6.1** specifies the `all-MiniLM-L6-v2` model but claims it produces `768-dim` embeddings and hardcodes `self.dimension = 768`. | **Critical.** This is factually incorrect. `all-MiniLM-L6-v2` produces **384-dimensional** embeddings. This error would lead to runtime failures and dimension mismatch errors in the vector store. |
| **C-3** | **Contradictory File System Diagram** | **Section 5.3** shows a file system structure with `.faiss` and `.pkl` files. | **High.** This structure is specific to a FAISS implementation and directly contradicts the decision to use ChromaDB, which manages its own persistence in a directory. |

## 3. Architectural Deviations

The design deviates from the approved `architecture-mvp.md` in ways that compromise strategic goals.

1.  **Omission of Critical Guardrail Agents:**
    - **Issue:** The proposed design removes the `Validate Query` and `Validate Retrieved Data` nodes from the workflow. The agent flow is presented as a simple linear sequence (`Retriever` -> `Analysis` -> `Insight` -> `Report Builder`).
    - **Impact:** This is a major regression.
        - Removing `Validate Query` eliminates our primary defense against prompt injection and out-of-domain requests, which was a key security and efficiency measure.
        - Removing `Validate Retrieved Data` means the graph will proceed with analysis even if no relevant information was found, wasting resources and producing low-quality or empty reports.
    - **Required Action:** These nodes must be re-integrated into the workflow as defined in the architecture.

2.  **Ambiguous Orchestration Strategy:**
    - **Issue:** The design is unclear on whether it uses LangGraph or a custom orchestrator. It includes `langgraph` in the dependencies but also defines a custom `AgentOrchestrator`, `WorkflowEngine`, and a `BaseAgent` interface.
    - **Impact:** This ambiguity is confusing. The architectural decision was to use **LangGraph** to leverage its battle-tested state management, conditional routing, and observability. Building a custom orchestrator re-invents the wheel, adds maintenance overhead, and discards the benefits of the chosen framework.
    - **Required Action:** The design must explicitly commit to using LangGraph. The custom `BaseAgent` interface and `AgentOrchestrator` should be removed in favor of LangGraph's standard functional nodes that operate on the state object.

## 4. Technical Recommendations & Weaknesses

1.  **Refine Prompting Strategy:**
    - **Issue:** The prompt templates in Section 7.2 ask the LLM to return structured JSON directly within the prompt.
    - **Recommendation:** This is an outdated and less reliable method. The design should consistently use the `instructor` library (which is correctly included in the dependencies) for all structured LLM outputs. This offloads JSON formatting and validation to the tool, making prompts cleaner and outputs more reliable, aligning with the strategy in the original TDD (`technical-design-mvp.md`).

2.  **Simplify Pydantic Models for MVP:**
    - **Issue:** The Pydantic models in Section 4.2 are extremely detailed (e.g., `AnalysisResult` has 10+ fields).
    - **Recommendation:** For an MVP, this level of detail is brittle and increases the risk of LLM failure to populate all fields correctly. Start with the simpler, more robust schemas defined in `technical-design-mvp.md` (e.g., `SourceAnalysis` with just `source_id`, `summary`, and `contradictions`). We can add more detail in future iterations based on performance.

3.  **Clarify Project Structure:**
    - **Issue:** The project structure in Section 3 is inconsistent with the dependencies and code snippets.
    - **Recommendation:** The entire project structure diagram and component map must be redrawn to be consistent with the choice of ChromaDB and LangGraph.

## 5. Action Items for Revision

The author, Saro, must complete the following actions and resubmit the document for review:

1.  **Resolve All Contradictions:** Systematically review the entire document and ensure consistency. The choice of **ChromaDB** and **LangGraph** must be reflected in all sections (diagrams, text, code, dependencies).
2.  **Correct Technical Inaccuracies:** Fix the embedding dimension for `all-MiniLM-L6-v2` to **384**.
3.  **Re-align with Architecture:**
    - Re-introduce the `Validate Query` and `Validate Retrieved Data` nodes into the agent workflow diagram and implementation plan.
    - Remove all references to a custom `AgentOrchestrator`, `WorkflowEngine`, and `BaseAgent` interface. The design must be based on LangGraph's `StateGraph` and functional nodes.
4.  **Adopt Recommended Technical Patterns:**
    - Update all agent designs to use the `instructor` library for structured outputs, and revise prompt templates accordingly.
    - Simplify the Pydantic models to a level appropriate for an MVP.
5.  **Update Open Questions:** Remove questions that have already been decided (e.g., Q2 regarding FAISS vs. ChromaDB) and add any new, relevant open questions.
6.  **Perform a Thorough Self-Review:** Before resubmitting, perform a full read-through to catch any remaining inconsistencies.
