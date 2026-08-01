import pytest
from app.pipeline.execution_pipeline import ExecutionPipeline
from pathlib import Path

def test_execution_pipeline_runs_tools(tmp_path):
    pipeline = ExecutionPipeline()
    base_dir = Path(__file__).resolve().parents[1]
    file_path = base_dir / "samples" / "sales.xlsx"
    output_path = tmp_path / "test_output.xlsx"

    plan = {
        "tools": ["trend", "anomaly"]
    }

    result = pipeline.execute(str(file_path), plan, output_path=str(output_path))

    assert "analysis_results" in result
    assert "trend" in result["analysis_results"]