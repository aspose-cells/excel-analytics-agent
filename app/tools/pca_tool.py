from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.pca_analysis import PCAAnalysis
from typing import Any, Dict, List


def run_pca(values: List[float]) -> Dict[str, Any]:
    """Run PCA analysis on a list of values.

    Args:
        values: List of numeric values to analyze.

    Returns:
        Dict containing PCA analysis results.
    """
    try:
        return PCAAnalysis.analyze(values)
    except Exception as e:
        logger.error(f"PCA analysis failed: {e}")
        raise ToolNotFoundError(f"PCA analysis failed: {e}") from e

def register() -> Dict[str, Any]:
    """Register the PCA tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "pca": {
            "func": run_pca,
            "input": "dataframe"
        }
    }