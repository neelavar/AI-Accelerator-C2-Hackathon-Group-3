
# Documentation Templates

This folder contains concise, opinionated templates the team should use to document product, project, architecture, and implementation decisions. Using these templates keeps documentation consistent, discoverable, and actionable — which is important when working with AI-augmented workflows and multiple contributors.

Why use these templates
- Standard format: makes reviews faster and decisions easier to trace.
- Persona-ready: templates are designed to be used together with the AI personas in `docs/ai-personas/` (ask a persona to help fill a section).
- Lightweight: aimed at small projects and rapid iteration.

Available templates
- `10_prd-template.md` — Product Requirements Document (PRD) for small AI agent projects.
- `20_project-plan-template.md` — Project plan / backlog template with phase-wise tasks and AI persona assignments.
- `40_architecture-template.md` — High-level solution architecture template (agentic systems focused).
- `41_technical-design-template.md` — Technical Design Document (TDD) for implementation-level details.

How to use
1. Pick the template that matches your activity: PRD → Project Plan → Architecture → TDD.
2. If you use an AI persona, open the relevant persona file in `docs/ai-personas/` and copy suggested prompts or instructions to guide the persona when drafting content.
3. Keep entries short and actionable. Use bullet lists, acceptance criteria, and examples where useful.
4. Save project-specific docs under `docs/project-docs/<project-name>/` and reference templates used in the file header.

Best practices
- Use the status conventions in the project plan (☐/◐/☑) to track progress.
- Link PRs to the PRD or project plan when implementing features.
- Add example payloads or small fixtures to `docs/examples/` alongside template-based documentation.

Related docs
- `README.md` (project root) — project overview and contribution guidance.
- `CONTRIBUTING.md` — contribution rules and workflow (collaborators only; no direct commits to `main` or `develop`).

If you think a template is missing or should be improved, open an issue and propose the change using the relevant template (e.g., create a PRD or Architecture update describing the improvement).

