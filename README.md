# 📊 Excel Data Analysis Agent

An AI-powered Excel analysis system combining **LLM planning (GPT)** + **SciPy data analysis** + **Aspose.Cells rendering** to automatically analyze spreadsheets, detect anomalies, generate insights, and export enriched Excel reports.

It behaves like a lightweight **data analyst agent** for structured Excel files.

---

## 🚀 Features

### 🧠 AI Agent Capabilities
- Natural language → analysis plan (GPT planner)
- Automatic tool selection (trend, anomaly, forecasting, PCA, etc.)
- Multi-step execution pipeline
- **Self-improving** — learns from past executions, adjusts tool recommendations
- **Autonomous scheduling** — supports timed execution

### 📊 Data Analysis (SciPy + sklearn)
- Anomaly detection (Z-score based)
- Trend analysis (regression smoothing)
- FFT frequency analysis
- Correlation matrix
- PCA dimensionality reduction
- Forecasting (basic statistical models)
- Clustering (KMeans)
- Distribution analysis
- Seasonality detection
- Change point detection

### 📈 Excel Intelligence (Aspose.Cells)
- Highlight anomalies directly in Excel
- Write comments to cells
- Format reports automatically
- Render charts (trend lines, distributions)
- Multi-sheet output support

### 🤖 LLM Integration
- OpenAI-compatible planner
- Tool routing via prompt engineering
- Structured execution pipeline

### 🛡️ Engineering Excellence
- **S9/A9/P9/R9/V9** maturity rating across all dimensions
- 100% type-hinted codebase
- Google-style docstrings on all public APIs
- Comprehensive error handling with circuit breaker + retry
- Performance benchmarks in CI
- Security scanning (safety + bandit)

---

## 🏗️ Architecture

```
User Request
   ↓
Planner (LLM)
   ↓
Tool Selection Plan
   ↓
Execution Pipeline
   ↓
SciPy / Sklearn Tools
   ↓
Excel Renderer (Aspose)
   ↓
Output Excel + Insights
```

---

## 📁 Project Structure

```
app/
  agents/                # Excel AI Agent core
  analysis/              # SciPy-based analytics
  excel/                 # Aspose Excel reader/writer/renderer
  llm/                   # Planner + prompts + explanation generator
  pipeline/              # execution / routing / reporting pipelines
  registry/              # tool registry
  tools/                 # wrapped tool interfaces
  learning.py            # Self-improvement engine
  resilience.py          # Circuit breaker + retry + fallback
  scheduler.py           # Autonomous task scheduling
  health.py              # Health check registry
  state.py               # Session state persistence
  logger.py              # Unified logging framework
  exceptions.py          # Custom exception hierarchy

tests/
  benchmarks/            # Performance benchmarks

scripts/
  security_scan.py       # Automated security scanning
  maturity_score.py      # S/A/P/R/V maturity assessment

docs/
  compliance/            # Compliance framework
  verification/          # Verification plan
  assurance/             # Assurance statement

docker/                  # Containerization
.github/                 # GitHub Actions + CODEOWNERS
```

---

## ⚙️ Installation

### 1. Clone repo

```bash  
git clone https://github.com/yourname/excel-ai-agent.git
cd excel-ai-agent
```

### 2. Install dependencies

```bash 
pip install -r requirements.txt
```

Required packages:
- aspose-cells-python
- openai
- numpy
- pandas
- scipy
- scikit-learn
- statsmodels
- python-dotenv
- pytest

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

---

## ▶️ Run Locally

### Run full agent

```bash  
python main.py
```

### Run tests

```bash 
pytest tests/ -v
```

### Run performance benchmarks

```bash
pytest tests/benchmarks/ -v
```

### Run security scan

```bash
python scripts/security_scan.py
```

### Run maturity assessment

```bash
python scripts/maturity_score.py
```

---

## 🧪 Core Pipeline

### 1. Planner

Transforms natural language into tool plan, e.g.:

```python
["trend", "anomaly"]
```

### 2. Execution Pipeline

Runs tools:
- column-based analysis (trend, anomaly, forecast)
- dataframe-based analysis (PCA, clustering)

### 3. Excel Renderer

Applies:
- formatting
- chart rendering
- comment injection

---

## 📊 Tool Registry

### Plugin Architecture

```
tools/*.py
        ↓
TOOL_REGISTRY
        ↓
Execution Pipeline
        ↓
LLM Planner
```

| Input Type  | Description                     |
| ----------- | ------------------------------- |
| `series`    | Single numeric column analysis  |
| `dataframe` | Multi-column dataframe analysis |

---

## 🐳 Docker Support

```bash  
docker build -f docker/Dockerfile -t excel-ai-agent .
docker-compose -f docker/docker-compose.yml up
```

---

## ⚙️ CI/CD

### GitLab CI (11 stages)

```
lint → test → code_quality → security → validate → score → ai_eval → quality_gate → build → deploy_staging → deploy_production
```

All stages include automated maturity scoring, security scanning, and quality gates.
Minimum score threshold: 30. Deploy requires passing quality gate.

---

## 🔥 What Makes This Special

Most "AI Excel tools":
> call GPT → summarize → done

This system:
- actually executes statistical analysis (SciPy)
- applies deterministic anomaly detection
- writes back to Excel (Aspose)
- supports multi-tool reasoning
- **self-improves** from past executions
- **self-heals** with circuit breakers and retry
- is CI/CD + Docker ready

So it behaves less like a chatbot  
and more like a **production-grade data analyst pipeline system**

---

## 📄 License

All examples use Aspose.Cells for Python via .NET.The examples can be evaluated using the free evaluation version. A valid license is recommended for production use. For licensing details, please refer to the Aspose website.
---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
Code ownership defined in [CODEOWNERS](.github/CODEOWNERS).
Security policies in [SECURITY.md](SECURITY.md).
Changelog in [CHANGELOG.md](CHANGELOG.md).