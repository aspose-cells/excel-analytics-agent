import numpy as np
from app.logger import logger
from app.exceptions import AnalysisError


class AnomalyAnalysis:
    """Detect anomalies in data using statistical methods."""

    @staticmethod
    def detect_zscore(values: list[float], threshold: float = 3) -> list[dict]:
        """Detect anomalies using the modified Z-score method.

        Args:
            values: List of numeric values to analyze.
            threshold: Z-score threshold for anomaly detection (default 3).

        Returns:
            List of dicts with keys: index, value, zscore for each anomaly.

        Raises:
            AnalysisError: If analysis fails.
        """
        try:
            arr = np.array(values, dtype=float)

            median = np.median(arr)
            mad = np.median(np.abs(arr - median))

            if mad == 0:
                return []

            modified_z = 0.6745 * (arr - median) / mad
            z_scores = np.abs(modified_z)

            anomalies = []

            for i, z in enumerate(z_scores):
                if z > threshold:
                    anomalies.append({
                        "index": i,
                        "value": float(arr[i]),
                        "zscore": float(z)
                    })

            return anomalies
        except Exception as e:
            logger.error("Anomaly detection failed: %s", e)
            raise AnalysisError(f"Anomaly detection failed: {e}") from e