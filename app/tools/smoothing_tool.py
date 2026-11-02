from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.smoothing import SmoothingAnalysis
from typing import Any, Dict, List


def run_smoothing(values: List[float]) -> List[float]:
    """Smooth a list of values with a moving average.

    Args:
        values: List of numeric values to smooth.

    Returns:
        List of smoothed values (NaN for the first window-1 positions).
    """
    try:
        return SmoothingAnalysis.moving_average(values)
    except Exception as e:
        logger.error(f"Smoothing analysis failed: {e}")
        raise ToolNotFoundError(f"Smoothing analysis failed: {e}") from e


def register() -> Dict[str, Any]:
    """Register the smoothing tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "smoothing": {
            "func": run_smoothing,
            "input": "series"
        }
    }
