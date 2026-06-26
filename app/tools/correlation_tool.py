from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.correlation import CorrelationAnalysis
from typing import Any, Dict, List


def run_correlation(values: List[float]) -> Dict[str, Any]:
    """Run correlation analysis on a list of values.

    Args:
        values: List of numeric values to analyze.

    Returns:
        Dict containing correlation matrix.
    """
    try:
        return CorrelationAnalysis.correlation_matrix(values)
    except Exception as e:
        logger.error(f"Correlation analysis failed: {e}")
        raise ToolNotFoundError(f"Correlation analysis failed: {e}") from e

def register() -> Dict[str, Any]:
    """Register the correlation tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "correlation": {
            "func": run_correlation,
            "input": "dataframe"
        }
    }