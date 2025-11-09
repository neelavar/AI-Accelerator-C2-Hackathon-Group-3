# UI/UX Design Decisions for MediScout MVP

This document outlines the key User Interface (UI) and User Experience (UX) design decisions made during the development of the MediScout MVP, focusing on enhancing usability, clarity, and interactivity.

---

## 1. Overall Application Layout: Tabbed Interface

**Decision:** Transitioned from a sidebar-based layout to a two-tab interface.
*   **Tab 1: "🧠 Knowledge Base"**: Dedicated to managing user-provided documents.
*   **Tab 2: "🔍 Research & Analysis"**: Dedicated to initiating research queries and displaying reports.

**Rationale:**
*   **Improved Space Utilization:** Tabs provide more horizontal space, which was restrictive in the sidebar for complex components like the Document Workbench.
*   **Clear Workflow Separation:** Distinct tabs clearly separate the two primary user workflows (document management vs. research execution), making the application easier to navigate.
*   **Enhanced Focus:** Users can focus on one task at a time without distractions from other sections.

---

## 2. Knowledge Base Management: The "Document Workbench"

**Decision:** Replaced the simple file uploader and static list with an interactive "Document Workbench" featuring card-based display and enhanced controls.

**Rationale:**
*   **User-Friendly & Innovative:** Provides a more engaging and intuitive way to manage documents.
*   **Scalability:** Addresses concerns about handling a large number of files gracefully.

### 2.1. Document Display: Interactive Cards in a Scrollable Grid

**Decision:** Each uploaded document is represented by an interactive card within a responsive, scrollable grid.

**Implementation Details:**
*   **Card Structure:** Each card displays the file icon, filename, and indexing status.
*   **Responsive Grid:** Uses `st.columns` to arrange cards in a grid (e.g., 3 columns).
*   **Scrollable Container:** The entire card grid is enclosed within an `st.container()` with a fixed `max-height` and `overflow-y: auto` (via custom CSS). This ensures a vertical scrollbar appears when content exceeds the height, preventing the page from becoming excessively long.

**Rationale:**
*   **Visual Clarity:** Cards offer a richer visual representation than a simple list, making it easier to distinguish and interact with individual documents.
*   **Space Efficiency:** The scrollable container effectively manages screen real estate, allowing for a large number of documents to be displayed without overwhelming the user.

### 2.2. Document Actions: Preview and Remove

**Decision:** Integrated direct actions ("Preview" and "Remove") onto each document card.

**Implementation Details:**
*   **"Preview" Button:** Clicking this button opens an `st.dialog` (modal-like pop-up).
    *   **Clear Marking:** The dialog has a prominent title (e.g., "Preview: `filename.pdf`") and displays the first 20-30 lines of the document's content within an `st.code` block for clear readability.
*   **"Remove" Button:** Clicking this button removes the corresponding file from the current selection in the session state.

**Rationale:**
*   **Direct Interaction:** Users can perform actions on individual documents without navigating away or using complex multi-select options.
*   **Immediate Feedback:** Actions are directly tied to the visual representation of the document.
*   **Enhanced Usability:** The clearly marked preview dialog ensures users understand they are viewing content and can easily close it.

### 2.3. Indexing Control: State-Aware and Auto-Sync

**Decision:** Implemented a more intelligent indexing mechanism with clear user guidance and an optional auto-synchronization feature.

**Implementation Details:**
*   **State-Aware Prompting:** The UI now detects changes in the `st.file_uploader` selection (files added or removed) compared to the last successfully indexed set. If a discrepancy is found, an `st.info` message prompts the user to "Sync & Index Knowledge Base."
*   **"Sync & Index Knowledge Base" Button:** Replaced "Index Documents" to better reflect its role in synchronizing the current selection with the AI's knowledge base.
*   **"Enable Auto-Sync" Checkbox:** An `st.checkbox` (defaulting to `False`) allows users to opt into automatic re-indexing whenever file selections change.

**Rationale:**
*   **Intuitive Workflow:** Guides the user on when and how to update their knowledge base, preventing confusion about the AI's current context.
*   **User Control:** Provides flexibility for users to choose between manual control over indexing (for potentially slow operations) or a more seamless, automated experience.

---
