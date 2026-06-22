from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.clustering import ClusteringAnalysis
from typing import Any, Dict, List


def run_clustering(values: List[float]) -> Dict[str, Any]:
    """Run clustering analysis on a list of values.

    Args:
        values: List of numeric values to cluster.

    Returns:
        Dict containing cluster labels under the 'clusters' key.
    """
    try:
        labels = ClusteringAnalysis.cluster(values)
        return {
            "clusters": labels
        }
    except Exception as e:
        logger.error(f"Clustering analysis failed: {e}")
        raise ToolNotFoundError(f"Clustering analysis failed: {e}") from e

def register() -> Dict[str, Any]:
    """Register the clustering tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "clustering": {
            "func": run_clustering,
            "input": "series"
        }
    }