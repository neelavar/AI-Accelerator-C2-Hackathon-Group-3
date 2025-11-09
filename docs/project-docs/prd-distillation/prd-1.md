# Product Requirements Document (PRD): Multi-agent AI Deep Researcher

> This PRD outlines the requirements for a Minimum Viable Product (MVP) of the Multi-agent AI Deep Researcher, intended for the hackathon. The focus is on simplicity, a demonstrable workflow, and a quality outcome.

---

## 1. Project Overview
- **Project Name:** Multi-agent AI Deep Researcher (Medical Domain Focus)
- **Date:** 2025-11-07
- **Prepared by:** AI Software Product Analyst
- **Stakeholders:** Hackathon Team, Hackathon Judges
- **Summary:** This project is an AI research assistant that uses a team of specialized agents to conduct in-depth, multi-source investigations for medical researchers. It combines user-provided documents with web-sourced data to perform critical analysis, generate novel hypotheses, and produce structured reports.

## 2. Problem Statement
Medical researchers face a time-consuming and fragmented process for conducting deep research. They lack efficient tools to integrate their existing knowledge base (papers, notes) with new web-sourced information, perform critical analysis at scale, and uncover non-obvious connections in the data.

## 3. Objectives & Success Criteria
- **Objective 1:** Automate the research process of collating, summarizing, and analyzing medical information from multiple sources.
- **Objective 2:** Demonstrate the ability to uncover a hidden connection or generate a novel, data-driven hypothesis.
- **Objective 3:** Produce a structured, coherent, and useful research report as the final output.

- **Success Criteria (for Hackathon):**
    - [ ] A user can initiate a research task on a medical topic.
    - [ ] The system successfully processes at least one user-provided document and retrieves relevant data from the web.
    - [ ] The final output is a single, structured report that includes a summary, a critical analysis, and at least one plausible hypothesis.
    - [ ] The entire process is demonstrable in a live presentation.

## 4. User Stories & Acceptance Criteria

**US1: Knowledge Base Creation**
- **As a:** Medical Researcher,
- **I want:** to upload my library of documents (.txt, .pdf, .csv) and have them indexed into a persistent knowledge base,
- **So that:** the system has a rich, reusable foundation for all my research tasks.
- **Acceptance Criteria:**
    - [ ] The UI has a "Setup & Indexing" section.
    - [ ] User can upload one or more supported files.
    - [ ] A button triggers the indexing process, which saves or updates a vector store file on disk.
    - [ ] The UI displays a list of successfully indexed file names.
    - [ ] The system shows a clear error message for unsupported file types (e.g., scanned images) without crashing.

**US2: Research Execution**
- **As a:** Medical Researcher,
- **I want:** to enter a research topic and trigger the analysis with a single click,
- **So that:** the system can generate a comprehensive report using my knowledge base and fresh web data.
- **Acceptance Criteria:**
    - [ ] The UI has a "Research & Analysis" section.
    - [ ] User can type a topic into a text input field.
    - [ ] A "Generate Report" button starts the multi-agent process.
    - [ ] The process loads the pre-built vector store from disk.
    - [ ] The system queries the PubMed and openFDA APIs.

**US3: Progress Monitoring**
- **As a:** Medical Researcher,
- **I want:** to see the current status of the analysis (e.g., "Analyzing...", "Generating Report..."),
- **So that:** I have confidence the system is working on my request.
- **Acceptance Criteria:**
    - [ ] The UI displays the current agent/stage of the process after the report generation is triggered.

**US4: Report Consumption**
- **As a:** Medical Researcher,
- **I want:** to download the final, structured Markdown report,
- **So that:** I can easily review the findings, novel hypotheses, and sources.
- **Acceptance Criteria:**
    - [ ] A "Download Report" button appears when the process is complete.
    - [ ] The downloaded file is a well-formatted `.md` file.
    - [ ] The report contains the required sections: Executive Summary, Detailed Findings, Contradictions & Gaps, Generated Hypotheses, and Sources.

## 5. Key Features & Requirements

### Functional Requirements
- **F1: Document Indexing & Persistence**
    - Support `.txt`, `.pdf`, and `.csv` file ingestion.
    - Generate vector embeddings from the text content of supported files.
    - Save and load the vector store to/from a local file (e.g., using FAISS or ChromaDB).
    - Gracefully handle and report errors for unsupported files.
- **F2: Multi-Source Data Retrieval**
    - Query the local vector store based on the research topic.
    - Query the public PubMed and openFDA APIs with relevant keywords.
- **F3: Multi-Agent Analysis & Synthesis**
    - **Critical Analysis Agent:** Must summarize findings, label data by source ("User-Provided," "PubMed," "openFDA"), and validate information by checking for it in more than one source.
    - **Insight Generation Agent:** Must be able to form at least a two-step reasoning chain to propose a hypothesis.
- **F4: Report Generation**
    - Generate a single, well-structured Markdown file.
    - The report must contain the following sections: Executive Summary, Detailed Findings, Contradictions & Gaps, Generated Hypotheses, and Sources.

### Non-Functional Requirements
- **NF1: User Interface:** A simple, two-section Streamlit application that is clean, functional, and guides the user through the two-step workflow.
- **NF2: Performance:** The "Generate Report" step should feel responsive for a demo, ideally completing within 2 minutes.

## 6. User Flow / Process Diagram

1.  **Setup Phase (Pre-Demo Preparation):**
    - The user opens the Streamlit app and navigates to the **"Setup & Indexing"** section.
    - The user uploads a batch of local research documents.
    - The user clicks "Add to Knowledge Base."
    - The system processes the files and saves/updates the vector store on the local disk. The UI confirms which files were indexed.

2.  **Research Phase (Live Demo):**
    - The user navigates to the **"Research & Analysis"** section.
    - The user enters a specific research topic (e.g., "GIST preventative factors").
    - The user clicks "Generate Report."
    - The system provides real-time status updates (e.g., "Loading knowledge base...", "Querying PubMed...", "Running analysis...").
    - When the process is complete, a "Download Report" button appears.
    - The user clicks the button to download the final Markdown report.

## 7. Feature Scope Matrix (MVP)

| Feature Area                 | Feature Description                                   | In Scope (MVP) | Out of Scope (MVP) |
|:-----------------------------|:------------------------------------------------------|:---------------|:-------------------|
| **User Provided Documents**  | Upload `.txt`, `.pdf`, `.csv` files                 | Yes            | No                 |
|                              | Upload `.doc`, `.docx`, `.ppt`, images, audio       | No             | Yes                |
|                              | Error handling for unsupported/unreadable files       | Yes            | No                 |
| **Knowledge Base (KB)**      | Persistent vector store (e.g., FAISS, ChromaDB)     | Yes            | No                 |
|                              | UI for managing (list, delete, update) individual KB files | No             | Yes                |
| **Web Data Sources**         | PubMed API integration                                | Yes            | No                 |
|                              | openFDA API integration                               | Yes            | No                 |
|                              | Other web sources (e.g., arXiv, general news APIs)    | No             | Yes                |
| **Agent Functionality**      | Contextual Retriever Agent (local KB + web)           | Yes            | No                 |
|                              | Critical Analysis Agent (summarize, validate, flag contradictions) | Yes            | No                 |
|                              | Insight Generation Agent (propose hypotheses via reasoning) | Yes            | No                 |
|                              | Report Builder Agent (compile structured Markdown)    | Yes            | No                 |
| **Report Generation**        | Markdown output format                                | Yes            | No                 |
|                              | Fixed report structure (Exec. Summary, Findings, etc.)| Yes            | No                 |
|                              | User-defined report templates                         | No             | Yes                |
| **User Interface**           | Streamlit App                                         | Yes            | No                 |
|                              | Two-section UI (Setup & Indexing, Research & Analysis)| Yes            | No                 |
|                              | Complex UI (job lists, persistent history, func. area selection) | No             | Yes                |
| **Core Goal**                | Find hidden connections/generate hypotheses           | Yes            | No                 |

## 8. Out of Scope
- User accounts and authentication.
- A polished, production-grade user interface.
- Support for non-English languages.
- Real-time, continuous monitoring of sources.
- Processing of scanned image documents that require OCR.
- Support for a large number of concurrent users.

## 9. Dependencies & Risks
- **Dependencies:**
    - Access to a public medical database/API (e.g., PubMed).
    - A stable LLM for agent reasoning and generation.
    - Python environment with necessary libraries (e.g., LangChain/LlamaIndex).
- **Risks:**
    - The chosen web source/API may be unreliable or have strict rate limits.
    - The LLM may hallucinate or generate low-quality, irrelevant content.
    - Integrating the four agents into a seamless workflow may be complex.

---
