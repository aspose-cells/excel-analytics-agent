from app.analysis.trend import TrendAnalysis

def test_trend_basic():
    data = [1, 2, 3, 4, 5]

    result = TrendAnalysis.analyze(data)

    assert "slope" in result
    assert isinstance(result["slope"], float)