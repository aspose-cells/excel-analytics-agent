from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.statistics_analysis import StatisticsAnalysis
from typing import Any, Dict, List


def run_statistics(values: List[float]) -> Dict[str, Any]:
    """Run statistical description on a list of values.

    Args:
        values: List of numeric values to describe.

    Returns:
        Dict containing statistical summary.
    """
    try:
        return StatisticsAnalysis.describe(values)
    except Exception as e:
        logger.error(f"Statistics analysis failed: {e}")
        raise ToolNotFoundError(f"Statistics analysis failed: {e}") from e

def register() -> Dict[str, Any]:
    """Register the statistics tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "statistics": {
            "func": run_statistics,
            "input": "series"
        }
    }