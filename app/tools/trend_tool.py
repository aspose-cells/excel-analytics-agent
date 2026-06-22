from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.trend import TrendAnalysis
from typing import Any, Dict, List


def run_trend(values: List[float]) -> Dict[str, Any]:
    """Run trend analysis on a list of values.

    Args:
        values: List of numeric values to smooth and analyze.

    Returns:
        Dict containing trend analysis results.
    """
    try:
        return TrendAnalysis.smooth(values)
    except Exception as e:
        logger.error(f"Trend analysis failed: {e}")
        raise ToolNotFoundError(f"Trend analysis failed: {e}") from e

def register() -> Dict[str, Any]:
    """Register the trend analysis tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "trend": {
            "func": run_trend,
            "input": "series"
        }
    }