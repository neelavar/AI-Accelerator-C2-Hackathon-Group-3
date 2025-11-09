# 📊 How to View MediScout Architecture

Sorry about the draw.io issue! I've created **3 different formats** so you can definitely view the architecture:

---

## ✅ **Option 1: HTML (EASIEST - Works 100%!)**

**File:** `architecture-diagram.html`

### How to Open:
1. **Double-click** the file: `docs/architecture-diagram.html`
2. It will open in your default browser
3. ✨ **Full interactive diagram with colors!**

**What you'll see:**
- 5 color-coded layers (UI, Orchestration, Agents, KB, External Services)
- All components with details
- Data flow explanation
- Performance metrics
- Tech stack table
- Print-friendly!

---

## ✅ **Option 2: Markdown with Mermaid (GitHub/VS Code)**

**File:** `ARCHITECTURE-DIAGRAM.md`

### How to View:

**In VS Code:**
1. Open `docs/ARCHITECTURE-DIAGRAM.md`
2. Press `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Windows)
3. The Mermaid diagram will render automatically!

**On GitHub:**
1. Push the file to GitHub
2. View it online - Mermaid renders automatically

**What you'll see:**
- Interactive Mermaid diagram (flowchart)
- ASCII text diagrams (work everywhere!)
- Complete data flow
- Tech stack details
- Performance metrics

---

## ✅ **Option 3: Plain Text (Works Anywhere!)**

**File:** `ARCHITECTURE-DIAGRAM.md`

### How to View:
1. Open in **any text editor**
2. Scroll to the ASCII diagram section
3. You'll see a complete text-based architecture diagram

**Example:**
```
┌──────────────────────────────┐
│  USER INTERFACE LAYER        │
│  [Streamlit] [Progress] ...  │
└──────────────────────────────┘
           ↓
┌──────────────────────────────┐
│  ORCHESTRATION (LangGraph)   │
└──────────────────────────────┘
```

---

## 🎯 **Quick Comparison**

| Format | File | Best For | Difficulty |
|--------|------|----------|------------|
| **HTML** | `architecture-diagram.html` | **Quick viewing** | ⭐ Easiest |
| **Markdown** | `ARCHITECTURE-DIAGRAM.md` | **VS Code/GitHub** | ⭐⭐ Easy |
| **Draw.io** | `MediScout-Architecture.drawio` | **Editing** | ⭐⭐⭐ Advanced |

---

## 🚀 **Recommended: Use HTML!**

**Just double-click this file:**
```
docs/architecture-diagram.html
```

It will open in your browser with the **full, beautiful, color-coded architecture diagram**! 🎨

---

## 📋 **What's Included in All Versions**

1. **5 Layers:**
   - 🔵 User Interface (Streamlit components)
   - 🟡 Orchestration (LangGraph)
   - 🔴 Agents (4 agents with models)
   - 🟣 Knowledge Base (Document processing + embeddings + ChromaDB)
   - 🟢 External Services (OpenRouter, PubMed, LangSmith)

2. **Data Flows:**
   - Document upload flow
   - Research query flow
   - Progress update flow

3. **Tech Stack:**
   - Complete list of all technologies

4. **Performance Metrics:**
   - Speed: 3-5 seconds
   - Top-3 results
   - Cached model
   - Parallel search

---

## 🔧 **Still Having Issues?**

If none of these work, you can also:
1. **View on GitHub**: Push to repo and view online
2. **Screenshot**: I can describe each component in detail
3. **Video Call**: Share screen and I'll walk you through

But the **HTML file should definitely work** - just double-click it! 🎉

---

**TL;DR: Just open `docs/architecture-diagram.html` in your browser!**

