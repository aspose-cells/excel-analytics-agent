from app.analysis.anomaly import AnomalyAnalysis

def test_anomaly_detects_outlier():
    data = [10, 11, 12, 13, 5000, 14]

    result = AnomalyAnalysis.detect_zscore(data)

    assert len(result) > 0
    assert any(item["value"] == 5000 for item in result)