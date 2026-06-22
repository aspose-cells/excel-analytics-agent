import json
import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("[AI_EVAL] openai not installed, skipping")
    sys.exit(0)


def load_report(path="output/maturity_score.json"):
    p = Path(path)
    if not p.exists():
        print(f"[AI_EVAL] No score report found at {path}, skipping")
        return None
    with open(p) as f:
        return json.load(f)


def evaluate_dimension(client, dim_key, dim_desc, report, model):
    static = report.get(dim_key, {})
    static_score = static.get("score", 0)
    static_level = static.get("level", "N/A")
    metrics = report.get("metrics", {})

    prompt = f"""You are a software maturity assessor. Evaluate the following dimension for the project 'Excel AI Agent'.

Dimension: {dim_desc}
Current static analysis score: {static_score:.1f} (Level: {static_level})

Project context:
- {metrics.get('source_files', 0)} Python source files
- {metrics.get('app_files', 0)} application files
- {metrics.get('test_files', 0)} test files
- {metrics.get('total_functions', 0)} functions, {metrics.get('total_classes', 0)} classes
- Type-hinted functions: {metrics.get('hinted_functions', 0)}
- Docstring coverage: {metrics.get('docstring_items', 0)} items
- Logging in {metrics.get('files_with_logging', 0)} files
- Error handling in {metrics.get('files_with_error_handling', 0)} files

Respond with ONLY a JSON object:
{{ "ai_score": <0-100 float>, "rationale": "<2-3 sentence rationale>", "gaps": ["<gap1>", "<gap2>"] }}"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
        )
        content = resp.choices[0].message.content
        print(f"[AI_EVAL] {dim_key} evaluated with {model}")
        return content
    except Exception as e:
        print(f"[AI_EVAL] {model} failed for {dim_key}: {e}")
        return None


def parse_response(raw):
    if not raw:
        return None
    cleaned = raw.strip().strip("```json").strip("```").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print(f"[AI_EVAL] Failed to parse response: {cleaned[:100]}")
        return None


def main():
    report = load_report()
    if not report:
        sys.exit(1)

    primary = os.getenv("AI_EVAL_MODEL", "gpt-4o")
    fallback = os.getenv("AI_EVAL_FALLBACK", "gpt-4o-mini")

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )

    dimensions = {
        "agent_score": "S0-S9 Agent Score (product readiness, features, documentation, CI/CD, code quality)",
        "agentic": "A0-A9 Agentic Maturity (automation, LLM, pipeline, state, coordination, adaptation)",
        "practices": "P0-P9 Engineering Practices (structure, automation, observability, verification, resilience)",
        "readiness": "R0-R9 Operational Readiness (deployment, ownership, governance, compliance, audit)",
        "evidence": "V0-V9 Evidence Coverage (tests, validation, benchmarks, security scanning, audit trail)",
    }

    results = {}
    for dim_key, dim_desc in dimensions.items():
        static = report.get(dim_key, {})
        static_score = static.get("score", 0)
        static_level = static.get("level", "N/A")

        raw = evaluate_dimension(client, dim_key, dim_desc, report, primary)
        if not raw:
            raw = evaluate_dimension(client, dim_key, dim_desc, report, fallback)

        parsed = parse_response(raw)
        if parsed:
            results[dim_key] = parsed
        else:
            results[dim_key] = {
                "ai_score": static_score,
                "rationale": "AI evaluation unavailable, using static score",
                "gaps": [],
            }

    combined_key_map = {
        "agent_score": "Agent Score (S)",
        "agentic": "Agentic (A)",
        "practices": "Practices (P)",
        "readiness": "Readiness (R)",
        "evidence": "Evidence (V)",
    }

    final = {
        "project": report["project"],
        "timestamp": report["timestamp"],
        "static_analysis": report,
        "ai_evaluation": results,
        "combined_scores": {},
    }

    for dim_key in dimensions:
        static = report.get(dim_key, {})
        ai = results.get(dim_key, {})
        combined = static.get("score", 0) * 0.6 + ai.get("ai_score", 0) * 0.4
        final["combined_scores"][dim_key] = {
            "static_score": static.get("score", 0),
            "ai_score": ai.get("ai_score", 0),
            "combined_score": round(combined, 1),
            "ai_rationale": ai.get("rationale", ""),
            "gaps": ai.get("gaps", []),
            "adjusted_level": ai.get("adjusted_level", static.get("level", "N/A")),
        }

    output_path = Path("output/maturity_score_ai.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 60)
    print("  AI-Assisted Maturity Score Report (S/A/P/R/V)")
    print("=" * 60)
    print(f"  {'Dimension':<25} {'Static':<10} {'AI':<10} {'Combined':<10}")
    print(f"  {'-'*25} {'-'*10} {'-'*10} {'-'*10}")
    for dim_key, cs in final["combined_scores"].items():
        label = combined_key_map.get(dim_key, dim_key)
        print(f"  {label:<25} {cs['static_score']:<10.1f} {cs['ai_score']:<10.1f} {cs['combined_score']:<10.1f}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
