import os
import pytest
from app.llm.planner import Planner

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
def test_planner_returns_tools():
    planner = Planner()

    plan, token_usage = planner.create_plan("Analyze sales trends and detect anomalies")

    assert isinstance(plan, dict)
    assert len(plan) > 0
    assert isinstance(token_usage, int)