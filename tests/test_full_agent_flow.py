import os
import pytest
from app.pipeline.execution_pipeline import ExecutionPipeline
from app.llm.planner import Planner
from pathlib import Path

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
def test_full_flow(tmp_path):
    planner = Planner()
    pipeline = ExecutionPipeline()
    base_dir = Path(__file__).resolve().parents[1]
    file_path = base_dir / "samples" / "sales.xlsx"
    output_path = tmp_path / "sales_analysis.xlsx"
    plan, _ = planner.create_plan("Analyze sales trends and detect anomalies")

    result = pipeline.execute(
        str(file_path), plan, output_path=str(output_path)
    )

    # The test must never write back into samples/sales.xlsx
    assert output_path.exists()
    assert "analysis_results" in result
    assert result["row_count"] > 0