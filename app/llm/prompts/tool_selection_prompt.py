from app.logger import logger

TOOL_SELECTION_PROMPT = """
You are a scientific Excel analysis planner.

You MUST output valid JSON only.

Schema:
{
  "tools": ["anomaly", "regression", "poly_regression", "trend", "fft", "statistics", "forecast", "arima", "clustering", "seasonality", "correlation", "pca", "hypothesis"],
  "reason": string,
  "confidence": number (0-1)
}

Do NOT return:
- list
- string
- markdown
- explanation

Rules:
- Only select tools that are necessary
- Prefer 2–4 tools max
- Do NOT include explanations outside JSON
"""