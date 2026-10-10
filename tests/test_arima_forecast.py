import numpy as np
import pytest
from app.analysis.arima_forecast import ARIMAForecast
from app.exceptions import AnalysisError


def test_forecast_trend_data():
    np.random.seed(42)
    trend = list(range(50))
    result = ARIMAForecast.forecast(trend, steps=5)

    assert isinstance(result, dict)
    assert "forecast" in result
    assert "order" in result
    assert "aic" in result
    assert "steps" in result
    assert len(result["forecast"]) == 5
    assert result["steps"] == 5
    assert result["order"] == [1, 1, 1]


def test_forecast_periodic_data():
    np.random.seed(42)
    x = np.arange(60)
    periodic = (10 * np.sin(2 * np.pi * x / 12) + np.random.normal(0, 1, 60)).tolist()
    result = ARIMAForecast.forecast(periodic, steps=6)

    assert len(result["forecast"]) == 6
    assert all(isinstance(v, float) for v in result["forecast"])


def test_forecast_custom_order():
    np.random.seed(42)
    data = np.random.randn(50).tolist()
    result = ARIMAForecast.forecast(data, steps=3, order=(2, 1, 0))

    assert result["order"] == [2, 1, 0]
    assert len(result["forecast"]) == 3


def test_forecast_returns_float_values():
    np.random.seed(42)
    data = np.random.randn(30).tolist()
    result = ARIMAForecast.forecast(data, steps=5)

    for val in result["forecast"]:
        assert isinstance(val, float)


def test_forecast_insufficient_data():
    short_data = [1.0, 2.0, 3.0]
    with pytest.raises(AnalysisError):
        ARIMAForecast.forecast(short_data, steps=3)


def test_forecast_single_step():
    np.random.seed(42)
    data = np.random.randn(50).tolist()
    result = ARIMAForecast.forecast(data, steps=1)

    assert len(result["forecast"]) == 1
    assert result["steps"] == 1
