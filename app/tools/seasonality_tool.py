from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.seasonality import SeasonalityAnalysis
from typing import Any, Dict, List


def run_seasonality(values: List[float]) -> Dict[str, Any]:
    """Decompose a time series into trend, seasonal and residual parts.

    Args:
        values: List of numeric time series values.

    Returns:
        Dict containing trend, seasonal and residual lists.
    """
    try:
        return SeasonalityAnalysis.analyze(values)
    except Exception as e:
        logger.error(f"Seasonality analysis failed: {e}")
        raise ToolNotFoundError(f"Seasonality analysis failed: {e}") from e


def register() -> Dict[str, Any]:
    """Register the seasonality tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "seasonality": {
            "func": run_seasonality,
            "input": "series"
        }
    }
