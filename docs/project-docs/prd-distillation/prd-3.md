# Product Requirements Document (PRD)

## 1. Project Overview
- **Project Name:** Multi-agent AI Deep Researcher (Medical Domain Focus)
- **Date:** (update as needed)
- **Prepared by:** Software Product Analyst (derived from `docs/ai-personas/10_software-product-analyst.md`)
- **Stakeholders:** Medical researchers, clinician-research teams, solution architect, developer team
- **Summary:** A prototype multi-agent system that ingests user-provided medical documents and curated web sources, performs critical analysis, synthesizes insights, and generates structured research reports to accelerate deep medical research.

## 2. Problem Statement
Medical researchers currently spend significant time manually searching diverse sources, validating provenance, synthesizing findings, and producing structured reports. There is a need for a reproducible tool that combines private document ingestion with curated web retrieval and multi-agent critical analysis to surface high-value, evidence-backed insights.

## 3. Objectives & Success Criteria
- Objectives:
  - Implement four cooperating agents: Contextual Retriever, Critical Analysis, Insight Generator, Report Builder.
  - Support private ingestion of user documents and retrieval from curated public sources.
  - Produce explainable insights with citations and reproducible report outputs.
- Success Criteria (MVP/prototype):
  - End-to-end demo run produces a final report from topic + uploaded documents.
  - Retrieval relevance: manual precision@5 >= 0.6 on demo topics (informal check).
  - Insight quality: at least one novel, plausible hypothesis produced per demo topic (qualitative evaluation).
  - Report completeness: generated report contains Executive Summary, Methods, Findings, Insights/Hypotheses, Citations.

## 4. User Stories & Acceptance Criteria
- User Story 1:
  - As a medical researcher, I want to upload my library of papers and a research topic so that the system returns a concise, cited summary and candidate hypotheses.
  - Acceptance Criteria:
    - [ ] Upload accepts PDF/text and indexes documents.
    - [ ] System returns a ranked list of top-10 relevant documents (mix of user docs + web results).
    - [ ] Final report includes citations to source ids/URLs.

- User Story 2:
  - As a researcher, I want contradictions and low-confidence sources flagged so I can prioritize validation.
  - Acceptance Criteria:
    - [ ] Analysis agent outputs per-source reliability notes and flags contradictions/uncertainties.

- User Story 3:
  - As a reviewer, I want hypotheses accompanied by supporting evidence and a short rationale.
  - Acceptance Criteria:
    - [ ] Insight agent produces 1–3 candidate hypotheses with supporting source pointers and a brief reasoning trace.

## 5. Key Features & Requirements
- Feature: Document ingestion & indexing
  - Requirement: Accept PDF/text uploads, extract plain text, and generate lightweight indexes for retrieval.
- Feature: Contextual retrieval
  - Requirement: Query user docs + curated external sources (e.g., PubMed) and rank results.
- Feature: Critical analysis
  - Requirement: Summarize individual sources, annotate provenance, and detect contradictions.
- Feature: Insight generation
  - Requirement: Synthesize cross-source evidence to propose hypotheses with confidence markers.
- Feature: Report builder
  - Requirement: Assemble structured report (Markdown/PDF) with sections and citations.

Non-functional requirements:
- Demo-friendly latency (steps complete in seconds-to-minutes for small datasets).
- Explainability: every insight must reference source ids/URLs and include a short rationale.
- Privacy: user-uploaded documents remain local to demo environment by default.

## 6. User Flow / Process Diagram
1. User uploads documents (single ZIP or multiple files) and enters a research topic.
2. Retriever indexes user docs and queries curated web sources.
3. Analysis agent summarizes and validates sources.
4. Insight agent synthesizes evidence and proposes hypotheses.
5. Report Builder compiles the final report for review/download.

## 7. Out of Scope
- Production-grade crawling or broad web scraping beyond curated sources (e.g., PubMed).
- Model fine-tuning or production deployments.
- Full regulatory/compliance support (e.g., HIPAA workflows) for the hackathon MVP.

## 8. Dependencies & Risks
- Dependencies:
  - Access to curated medical sources (PubMed APIs or curated datasets).
  - Text extraction library for PDFs (e.g., pdfminer or similar) if implemented.
- Risks & Mitigations:
  - Low-quality or paywalled sources → prioritize curated sources and annotate provenance.
  - Misleading hypotheses → label as hypotheses with confidence levels and require human validation.
  - Privacy concerns → keep uploads local and avoid cloud unless approved.

## 9. Backlog (priority)
1. Create `docs/examples/` with a small sample topic + 1–3 short example papers.
2. Scaffold prototype package `researcher_agents/` and placeholder scripts for each agent.
3. Implement ingestion + retrieval POC with sample data.
4. Implement summarization + validation heuristics.
5. Implement insight synthesis and basic report templating.

---
*Use this file as a living document. For formalization, align with `docs/templates/10_prd-template.md`.*

