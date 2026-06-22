from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.anomaly import AnomalyAnalysis
from typing import Any, Dict, List


def run_anomaly(values: List[float]) -> Dict[str, Any]:
    """Run anomaly detection on a list of values.

    Args:
        values: List of numeric values to analyze.

    Returns:
        Dict containing anomaly detection results.
    """
    try:
        return AnomalyAnalysis.detect_zscore(values)
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        raise ToolNotFoundError(f"Anomaly detection failed: {e}") from e

def register() -> Dict[str, Any]:
    """Register the anomaly detection tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "anomaly": {
            "func": run_anomaly,
            "input": "series"
        }
    }