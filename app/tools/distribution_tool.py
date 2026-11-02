from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.distribution import DistributionAnalysis
from typing import Any, Dict, List


def run_distribution(values: List[float]) -> Dict[str, Any]:
    """Run a normality test on a list of values.

    Args:
        values: List of numeric values to test.

    Returns:
        Dict containing statistic, pvalue and is_normal.
    """
    try:
        return DistributionAnalysis.check_normal_distribution(values)
    except Exception as e:
        logger.error(f"Distribution analysis failed: {e}")
        raise ToolNotFoundError(f"Distribution analysis failed: {e}") from e


def register() -> Dict[str, Any]:
    """Register the distribution tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "distribution": {
            "func": run_distribution,
            "input": "series"
        }
    }
