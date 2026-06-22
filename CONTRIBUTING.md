# Contributing to Excel AI Agent

Thank you for your interest in contributing! This document provides guidelines for contributions.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Adding a New Analysis Tool](#adding-a-new-analysis-tool)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [CI/CD Pipeline](#cicd-pipeline)

## Code of Conduct

This project follows a standard open source code of conduct. Be respectful, constructive, and inclusive.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/excel-ai-agent.git`
3. Set up the development environment (see below)

## Development Setup

### Prerequisites

- Python 3.11+
- An OpenAI-compatible API key

### Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Verify setup
python scripts/validate_env.py
```

## Project Structure

```
app/
  agents/          # Agent orchestration
  analysis/        # Scientific computing modules
  excel/           # Aspose.Cells I/O and rendering
  llm/             # LLM planner and prompts
  pipeline/        # Execution/routing/report pipelines
  registry/        # Dynamic tool registry
  tools/           # Tool wrappers (plugin architecture)
tests/             # Unit and integration tests
scripts/           # Dev utilities
docker/            # Containerization
```

## Adding a New Analysis Tool

The tool registry auto-discovers tools via `pkgutil`. To add a new analysis:

1. Create a new file in `app/tools/` (e.g., `new_analysis_tool.py`)
2. Implement a `register()` function:

```python
def register():
    return {
        "tool_name": {
            "func": run_function,
            "input": "series"  # or "dataframe"
        }
    }

def run_function(df, column):
    # Your analysis logic here
    return results
```

3. Add any new analysis logic to `app/analysis/`
4. Add tests in `tests/`

## Coding Standards

### Style

- Follow PEP 8
- Maximum line length: 120 characters
- Use 4-space indentation

### Type Hints

All function signatures must include type hints:

```python
def analyze_trend(data: pd.Series, threshold: float = 0.05) -> dict:
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def analyze(data: pd.Series) -> dict:
    """Perform trend analysis on the given data.

    Args:
        data: Input time series data.

    Returns:
        dict: Analysis results with keys 'trend', 'slope', 'intercept'.
    """
```

### Logging

Use the `logging` module instead of `print`:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Analysis completed for column: %s", column)
```

## Testing

All contributions must include tests.

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term

# Run specific test
pytest tests/test_anomaly.py -v
```

### Test Requirements

- New tools must have unit tests
- Bug fixes must include a regression test
- Pipeline changes must pass integration tests
- Minimum coverage threshold: 80%

## Commit Messages

Follow conventional commits:

```
type(scope): description

feat(tools): add FFT frequency analysis tool
fix(planner): handle null response from LLM
docs(readme): update installation instructions
test(anomaly): add edge case for empty series
refactor(pipeline): extract shared validation logic
ci(gitlab): add security scanning stage
```

## Pull Request Process

1. Create a feature branch from `main`: `git checkout -b feat/my-feature`
2. Make your changes and commit
3. Run tests locally: `pytest tests/ -v`
4. Push to your fork and open a PR
5. Ensure CI pipeline passes (lint → test → security → build)
6. Request review from the relevant code owners
7. Squash commits before merge

### PR Checklist

- [ ] Code follows coding standards
- [ ] Type hints added
- [ ] Tests added/updated
- [ ] Documentation updated if needed
- [ ] CI pipeline passes
- [ ] No hardcoded secrets or API keys

## CI/CD Pipeline

This project uses GitLab CI with the following stages:

```
lint → test → code_quality → security → validate → score → ai_eval → quality_gate → build → deploy
```

---

Thank you for contributing!
