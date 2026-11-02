from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.outlier import OutlierAnalysis
from typing import Any, Dict, List


def run_outlier(values: List[float]) -> List[Dict[str, Any]]:
    """Detect outliers on a list of values using the IQR method.

    Args:
        values: List of numeric values to analyze.

    Returns:
        List of outliers, each with index and value.
    """
    try:
        return OutlierAnalysis.iqr_outliers(values)
    except Exception as e:
        logger.error(f"Outlier detection failed: {e}")
        raise ToolNotFoundError(f"Outlier detection failed: {e}") from e


def register() -> Dict[str, Any]:
    """Register the outlier tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "outlier": {
            "func": run_outlier,
            "input": "series"
        }
    }
