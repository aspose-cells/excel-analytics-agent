from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.regression import RegressionAnalysis
from typing import Any, Dict, List


def run_regression(
    values: List[float],
    x_values: List[float] | None = None,
) -> Dict[str, Any]:
    """Run linear regression on a list of values.

    Args:
        values: List of numeric y-values for regression.
        x_values: Optional numeric x-values aligned with ``values``.

    Returns:
        Dict containing regression results.
    """
    try:
        return RegressionAnalysis.linear_regression(values, x_values=x_values)
    except Exception as e:
        logger.error(f"Regression analysis failed: {e}")
        raise ToolNotFoundError(f"Regression analysis failed: {e}") from e


def run_poly_regression(
    values: List[float],
    degree: int = 2,
    x_values: List[float] | None = None,
) -> Dict[str, Any]:
    """Run polynomial regression on a list of values.

    Args:
        values: List of numeric y-values for regression.
        degree: Polynomial degree (default 2).
        x_values: Optional numeric x-values aligned with ``values``.

    Returns:
        Dict containing polynomial regression results.
    """
    try:
        return RegressionAnalysis.polynomial_regression(
            values, degree=degree, x_values=x_values
        )
    except Exception as e:
        logger.error(f"Polynomial regression failed: {e}")
        raise ToolNotFoundError(f"Polynomial regression failed: {e}") from e

def register() -> Dict[str, Any]:
    """Register the regression tools in the tool registry.

    Returns:
        Dict describing the tools' functions and input types.
    """
    return {
        "regression": {
            "func": run_regression,
            "input": "series"
        },
        "poly_regression": {
            "func": run_poly_regression,
            "input": "series"
        },
    }