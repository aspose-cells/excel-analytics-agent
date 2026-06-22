from app.pipeline.execution_pipeline import ExecutionPipeline
from pathlib import Path

def test_execution_pipeline_runs_tools():
    pipeline = ExecutionPipeline()
    base_dir = Path(__file__).resolve().parents[1]
    file_path = base_dir / "samples" / "sales.xlsx"

    plan = {
        "tools": ["trend", "anomaly"]
    }

    result = pipeline.execute(str(file_path), plan)

    assert "analysis_results" in result
    assert "trend" in result["analysis_results"]