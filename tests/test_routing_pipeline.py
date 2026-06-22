from app.pipeline.routing_pipeline import RoutingPipeline

def test_tool_routing():
    router = RoutingPipeline()

    tools = router.route("../samples/sales.xlsx","Analyze sales trends and detect anomalies")

    assert "trend" in tools["tools"]
    assert "anomaly" in tools["tools"]