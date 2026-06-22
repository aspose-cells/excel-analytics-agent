from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.regression import RegressionAnalysis
from typing import Any, Dict, List


def run_regression(values: List[float]) -> Dict[str, Any]:
    """Run linear regression on a list of values.

    Args:
        values: List of numeric values for regression.

    Returns:
        Dict containing regression results.
    """
    try:
        return RegressionAnalysis.linear_regression(values)
    except Exception as e:
        logger.error(f"Regression analysis failed: {e}")
        raise ToolNotFoundError(f"Regression analysis failed: {e}") from e

def register() -> Dict[str, Any]:
    """Register the regression tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "regression": {
            "func": run_regression,
            "input": "series"
        }
    }