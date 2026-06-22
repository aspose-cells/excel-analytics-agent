from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.forecasting import ForecastingAnalysis
from typing import Any, Dict, List


def run_forecast(values: List[float]) -> Dict[str, Any]:
    """Run forecast analysis on a list of values.

    Args:
        values: List of numeric values to forecast.

    Returns:
        Dict containing forecast results.
    """
    try:
        return ForecastingAnalysis.forecast(values)
    except Exception as e:
        logger.error(f"Forecast analysis failed: {e}")
        raise ToolNotFoundError(f"Forecast analysis failed: {e}") from e

def register() -> Dict[str, Any]:
    """Register the forecast tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "forecast": {
            "func": run_forecast,
            "input": "series"
        }
    }