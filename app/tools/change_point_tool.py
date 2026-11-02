from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.change_point import ChangePointAnalysis
from typing import Any, Dict, List


def run_change_point(values: List[float]) -> List[Dict[str, Any]]:
    """Run change point detection on a list of values.

    Args:
        values: List of numeric values to analyze.

    Returns:
        List of change points, each with position and change magnitude.
    """
    try:
        return ChangePointAnalysis.detect(values)
    except Exception as e:
        logger.error(f"Change point detection failed: {e}")
        raise ToolNotFoundError(f"Change point detection failed: {e}") from e


def register() -> Dict[str, Any]:
    """Register the change point tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "change_point": {
            "func": run_change_point,
            "input": "series"
        }
    }
