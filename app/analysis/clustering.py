import numpy as np
from sklearn.cluster import KMeans
from app.logger import logger
from app.exceptions import AnalysisError


class ClusteringAnalysis:
    """Cluster data using K-Means algorithm."""

    @staticmethod
    def cluster(values: list[float], k: int = 3) -> list[int]:
        """Perform K-Means clustering on the given values.

        Args:
            values: List of numeric values to cluster.
            k: Number of clusters (default 3).

        Returns:
            List of cluster labels corresponding to each input value.

        Raises:
            AnalysisError: If clustering fails.
        """
        try:
            arr = np.array(values).reshape(-1, 1)

            model = KMeans(n_clusters=k, n_init=10)
            labels = model.fit_predict(arr)

            return labels.tolist()
        except Exception as e:
            logger.error("Clustering failed: %s", e)
            raise AnalysisError(f"Clustering failed: {e}") from e