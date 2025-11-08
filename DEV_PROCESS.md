# Development Process Guide - Hackathon Edition

## ⚡ Hackathon Timeline

**Start**: November 8, 2025
**End**: November 9, 2025 - 5:00 PM IST
**Duration**: ~33 hours

## 🎯 Critical Success Factors

1. **MVP First**: Working demo over perfect code
2. **Parallel Work**: Multiple team members working simultaneously
3. **Quick Decisions**: No lengthy debates, decide and move
4. **Core Features Only**: Focus on the 4 main agents
5. **Continuous Integration**: Push working code frequently

## 📋 Table of Contents

1. [Overview](#overview)
2. [Hackathon Workflow](#hackathon-workflow)
3. [Environment Setup](#environment-setup)
4. [Coding Standards](#coding-standards)
5. [Testing Strategy](#testing-strategy)
6. [Code Review Process](#code-review-process)
7. [Time Management](#time-management)
8. [Documentation](#documentation)

## Overview

This document outlines the **accelerated development process** for the Multi-Agent AI Deep Researcher hackathon project. We have approximately 33 hours to deliver a working MVP.

## Hackathon Workflow

### 1. Rapid Sprint Structure

- **Total Duration**: 33 hours (Nov 8 - Nov 9, 5 PM IST)
- **Quick Sync Meetings**: Every 3-4 hours
- **No Formal Sprints**: Continuous development

#### Project Board (Simplified)

- 🎯 **Critical (P0)**: Must have for demo
- 🚀 **In Progress**: Being worked on now
- ✅ **Done**: Completed and merged
- ❄️ **Nice to Have**: Only if time permits

### 2. Hackathon Development Cycle (Streamlined)

```
1. Assign task (claim in team chat)
   ↓
2. Create feature branch (optional for simple changes)
   ↓
3. Code + Basic testing
   ↓
4. Quick commit with clear message
   ↓
5. Push immediately
   ↓
6. Quick peer review (10-15 min max) OR self-merge for minor changes
   ↓
7. Merge and move on
```

### 3. Parallel Work Streams (Nov 8-9)

**Phase 1 (Hours 0-8): Foundation**
- Set up project structure
- Basic agent scaffolding
- API integrations setup
- Simple UI/CLI

**Phase 2 (Hours 8-20): Core Development**
- Implement all 4 agents
- Agent orchestration
- End-to-end flow
- Integration testing

**Phase 3 (Hours 20-28): Integration & Polish**
- Connect all components
- Bug fixes
- Demo preparation
- Documentation

**Phase 4 (Hours 28-33): Final Push**
- Final testing
- Demo rehearsal
- Presentation prep
- Buffer for issues

## Environment Setup

### Prerequisites

- Python 3.10 or higher
- Git 2.x or higher
- Virtual environment tool (venv, conda, etc.)
- IDE with Python support (VSCode, PyCharm recommended)

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd AI-Accelerator-C2-Hackathon-Group-3

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Install pre-commit hooks
pre-commit install

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables

Create a `.env` file with the following variables:

```env
# LLM API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Vector Database
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment

# External APIs
NEWSAPI_KEY=your_newsapi_key
SERPER_API_KEY=your_serper_key

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=True
```

## Coding Standards

### Python Style Guide

Follow **PEP 8** standards with these specifics:

- **Line Length**: 88 characters (Black formatter default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Organized and sorted with `isort`

### Code Formatting Tools

```bash
# Black - Code formatter
black src/ tests/

# isort - Import organizer
isort src/ tests/

# flake8 - Linting
flake8 src/ tests/

# mypy - Type checking
mypy src/
```

### Naming Conventions

```python
# Classes: PascalCase
class ContextualRetrieverAgent:
    pass

# Functions and methods: snake_case
def retrieve_research_papers():
    pass

# Constants: UPPER_CASE
MAX_RETRY_ATTEMPTS = 3

# Private methods: _leading_underscore
def _internal_helper():
    pass

# Type hints: Always use them
def process_query(query: str, max_results: int = 10) -> List[Document]:
    pass
```

### Documentation Standards

```python
def analyze_sources(sources: List[Document], threshold: float = 0.8) -> AnalysisResult:
    """
    Analyze multiple sources for credibility and contradictions.
    
    Args:
        sources: List of documents to analyze
        threshold: Credibility score threshold (0.0 to 1.0)
    
    Returns:
        AnalysisResult object containing summary and credibility scores
    
    Raises:
        ValueError: If threshold is not between 0 and 1
        
    Example:
        >>> sources = load_sources("climate_change")
        >>> result = analyze_sources(sources, threshold=0.7)
        >>> print(result.summary)
    """
    pass
```

## Testing Strategy (Hackathon Edition)

### Pragmatic Testing Approach

**Priority**: Functionality > Coverage

1. **Smoke Tests**: Basic functionality works
2. **Integration Tests**: Agents work together
3. **Manual Testing**: Quick checks before merging
4. **Unit Tests**: Only for critical functions

### Testing Requirements (Relaxed)

- **Coverage Target**: Nice to have, not required
- **Critical Features**: Must be tested
- **Demo Flow**: Must work reliably

### Quick Testing

```bash
# Test your component works
python -m pytest tests/test_your_component.py -v

# Quick integration check
python src/main.py --test

# Manual smoke test
python scripts/smoke_test.py
```

## Code Review Process (Fast Track)

### Rapid Review Rules

**For Critical Features (P0):**
- Self-merge allowed after basic testing
- Peer review in < 15 minutes
- Focus on "does it work?" not "is it perfect?"

**For Non-Critical:**
- Quick review via team chat
- Async approval OK
- Trust your teammates

### Quick PR Checklist

- [ ] Does it work?
- [ ] Does it break anything?
- [ ] Can we demo it?
- [ ] Clear commit message?

**If all yes → MERGE and move on!**

### When to Skip Review

- Documentation changes
- Minor bug fixes
- Configuration updates
- Your own component (if working)

### When Review is REQUIRED

- Core agent logic changes
- Breaking changes
- Security-related code
- Orchestration layer changes

## CI/CD Pipeline (Minimal for Hackathon)

### Local Checks Only

**Before Pushing (Optional):**
```bash
# Quick format (if you have time)
black src/

# Basic syntax check
python -m py_compile src/your_file.py
```

### GitHub Actions (Simplified)

- Basic linting (won't block merges)
- Automated on push (for tracking only)
- **Don't wait for CI to pass** - merge if it works locally

### Deployment

- **"Production"** = Your laptop for demo
- No deployment pipeline needed
- Focus on working demo, not infrastructure

## Time Management (Critical!)

### Hourly Breakdown (33 Hours Total)

**Nov 8 - Day 1 (~16 hours)**
- **09:00-12:00** (3h): Setup + Planning + Task assignment
- **12:00-14:00** (2h): Core infrastructure
- **14:00-18:00** (4h): Agent development (parallel)
- **18:00-19:00** (1h): Sync + Integration
- **19:00-23:00** (4h): Continue agent work
- **23:00-24:00** (1h): Daily wrap-up + sync
- **00:00-01:00** (1h): Buffer/breaks

**Nov 9 - Day 2 (~17 hours until 5 PM IST)**
- **09:00-12:00** (3h): Complete agent implementations
- **12:00-14:00** (2h): Integration + orchestration
- **14:00-16:00** (2h): End-to-end testing
- **16:00-17:00** (1h): Bug fixes
- **17:00-19:00** (2h): Demo preparation
- **19:00-21:00** (2h): Presentation + slides
- **21:00-22:00** (1h): Final rehearsal
- **22:00-17:00** (2h): Buffer for emergencies

### Time-Saving Tips

1. **Use pre-built libraries** - Don't reinvent the wheel
2. **Mock APIs first** - Use dummy data, integrate real APIs later
3. **Skip perfect formatting** - Code that works > pretty code
4. **Parallel development** - Don't block each other
5. **Standup every 3-4 hours** - Quick sync to unblock

### What to Cut if Running Late

**Cut First (Nice to Have):**
- Advanced visualization
- Multiple export formats (keep PDF only)
- Additional agents beyond core 4
- Perfect UI/UX
- Comprehensive error handling

**Cut Second (Important but not critical):**
- Unit tests (keep integration tests)
- Code documentation
- Multiple data sources (keep 1-2 working)

**Never Cut (Critical for Demo):**
- Core 4 agents working
- Basic orchestration
- One complete research flow
- Simple UI/CLI for demo
- Presentation slides

## Documentation (Minimal for Hackathon)

### What to Document (Priority Order)

1. **README.md**: How to run the demo
2. **Code comments**: Only for complex logic
3. **Demo script**: Step-by-step for presentation
4. **Setup instructions**: For judges to try it

### Skip for Now

- Detailed API documentation
- Architecture diagrams (unless quick)
- Extensive docstrings
- Auto-generated docs

## Best Practices (Hackathon Edition)

### 1. Speed Over Perfection

- **Working code** > Perfect code
- **Demo-ready** > Production-ready
- **Iterate fast** > Plan extensively

### 2. Communication is Key

```
🟢 GOOD: "I'm stuck on X, need help" (after 15 min)
🔴 BAD: Staying stuck for 2 hours silently

🟢 GOOD: "Feature X done, merging now"
🔴 BAD: Working in isolation for 6 hours

🟢 GOOD: "This is taking too long, switching approach"
🔴 BAD: Continuing down a dead-end path
```

### 3. Quick Error Handling

```python
# Hackathon style: Fail fast, show errors
try:
    result = api.fetch_data()
except Exception as e:
    print(f"Error: {e}")
    return None  # Or use dummy data
```

### 4. Simple Logging

```python
# Quick and dirty logging
print(f"[DEBUG] Retriever got {len(results)} results")
print(f"[ERROR] API call failed: {error}")
```

### 5. Security (Minimum Requirements)

- Use `.env` for API keys
- Don't commit `.env` file
- That's it for now - focus on functionality!

## Hackathon Survival Guide

### When Things Go Wrong (They Will!)

**Issue**: API rate limits
**Solution**: Use caching or mock data immediately

**Issue**: Agent not working
**Solution**: Simplify! Use hardcoded responses first, then iterate

**Issue**: Integration failing
**Solution**: Test each agent separately first, then combine

**Issue**: Running out of time
**Solution**: Cut features ruthlessly. Demo 1-2 agents well > 4 agents poorly

**Issue**: Team member blocked
**Solution**: Unblock IMMEDIATELY. Pair program or reassign task.

### Emergency Decisions

**If at Hour 20 and not integrated:**
- Cut to 2 agents minimum
- Use simple sequential flow
- Hardcode connections

**If at Hour 28 and bugs everywhere:**
- Document known issues
- Focus on one working demo path
- Have backup demo video

**If at Hour 30 and no UI:**
- Terminal output is fine!
- Or quick Streamlit app (30 min)

### Quick Wins

1. **Use templates**: LangChain has agent templates
2. **Steal from docs**: Copy-paste from official examples
3. **Mock first**: Get UI working with fake data
4. **Parallelize**: Never have idle team members

## Resources

- [Python PEP 8 Style Guide](https://pep8.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [Git Best Practices](https://git-scm.com/book/en/v2)
- [Code Review Best Practices](https://google.github.io/eng-practices/review/)

---

**Last Updated**: November 2025
**Maintained By**: Group 3 - AI Accelerator C2 Cohort

