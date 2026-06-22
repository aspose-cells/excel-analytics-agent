import time
import pytest


def test_anomaly_detection_speed():
    import numpy as np
    from app.analysis.anomaly import AnomalyDetection

    data = np.random.randn(10000).tolist()
    start = time.time()
    for _ in range(10):
        AnomalyDetection.detect(data, threshold=3.0)
    elapsed = time.time() - start
    assert elapsed < 5.0, f"Anomaly detection too slow: {elapsed:.2f}s"


def test_trend_analysis_speed():
    import numpy as np
    from app.analysis.trend import TrendAnalysis

    data = np.random.randn(10000).tolist()
    start = time.time()
    for _ in range(10):
        TrendAnalysis.analyze(data)
    elapsed = time.time() - start
    assert elapsed < 5.0, f"Trend analysis too slow: {elapsed:.2f}s"


def test_regression_speed():
    import numpy as np
    from app.analysis.regression import RegressionAnalysis

    x = list(range(1000))
    y = np.random.randn(1000).tolist()
    start = time.time()
    for _ in range(50):
        RegressionAnalysis.analyze(x, y)
    elapsed = time.time() - start
    assert elapsed < 5.0, f"Regression too slow: {elapsed:.2f}s"


def test_fft_speed():
    import numpy as np
    from app.analysis.fft_analysis import FFTAnalysis

    data = np.random.randn(5000).tolist()
    start = time.time()
    for _ in range(20):
        FFTAnalysis.analyze(data)
    elapsed = time.time() - start
    assert elapsed < 5.0, f"FFT too slow: {elapsed:.2f}s"


def test_clustering_speed():
    import numpy as np
    import pandas as pd
    from app.analysis.clustering import ClusteringAnalysis

    df = pd.DataFrame(np.random.randn(2000, 5), columns=[f"col{i}" for i in range(5)])
    start = time.time()
    for _ in range(10):
        ClusteringAnalysis.cluster(df, n_clusters=3)
    elapsed = time.time() - start
    assert elapsed < 10.0, f"Clustering too slow: {elapsed:.2f}s"
