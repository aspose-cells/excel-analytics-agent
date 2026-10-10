from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.arima_forecast import ARIMAForecast
from typing import Any, Dict, List


def run_arima(values: List[float]) -> Dict[str, Any]:
    """Run ARIMA forecasting on a list of values.

    Args:
        values: List of numeric time series values to forecast.

    Returns:
        Dict containing ARIMA forecast results.
    """
    try:
        return ARIMAForecast.forecast(values)
    except Exception as e:
        logger.error(f"ARIMA forecasting failed: {e}")
        raise ToolNotFoundError(f"ARIMA forecasting failed: {e}") from e


def register() -> Dict[str, Any]:
    """Register the ARIMA forecasting tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "arima": {
            "func": run_arima,
            "input": "series"
        }
    }
