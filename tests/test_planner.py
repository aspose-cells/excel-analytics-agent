from app.llm.planner import Planner

def test_planner_returns_tools():
    planner = Planner()

    result = planner.create_plan("Analyze sales trends and detect anomalies")

    assert isinstance(result, dict)
    assert len(result) > 0