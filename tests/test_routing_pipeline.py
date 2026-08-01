import os
import pytest
from app.pipeline.routing_pipeline import RoutingPipeline

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
def test_tool_routing():
    router = RoutingPipeline()

    tools, token_usage = router.route("../samples/sales.xlsx","Analyze sales trends and detect anomalies")

    assert "trend" in tools["tools"]
    assert "anomaly" in tools["tools"]
    assert isinstance(token_usage, int)