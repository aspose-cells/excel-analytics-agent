from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.kde import KDEAnalysis
from typing import Any, Dict, List


def run_kde(values: List[float]) -> Dict[str, Any]:
    """Run KDE density estimation and mode detection on a list of values.

    Args:
        values: List of numeric values for density estimation.

    Returns:
        Dict containing bandwidth, n_modes, mode_locations and
        is_multimodal.
    """
    try:
        return KDEAnalysis.estimate_density(values)
    except Exception as e:
        logger.error(f"KDE analysis failed: {e}")
        raise ToolNotFoundError(f"KDE analysis failed: {e}") from e


def register() -> Dict[str, Any]:
    """Register the KDE tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "kde": {
            "func": run_kde,
            "input": "series"
        }
    }
