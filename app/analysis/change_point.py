import numpy as np
from app.logger import logger
from app.exceptions import AnalysisError


class ChangePointAnalysis:
    """Detect change points in time series data."""

    @staticmethod
    def detect(values: list[float]) -> list[dict]:
        """Detect significant change points using difference thresholding.

        Args:
            values: List of numeric values to analyze.

        Returns:
            List of dicts with keys: position, change for each change point.

        Raises:
            AnalysisError: If analysis fails.
        """
        try:
            arr = np.array(values, dtype=float)

            diffs = np.diff(arr)

            threshold = np.std(diffs) * 2

            result = []

            for i, d in enumerate(diffs):
                if abs(d) > threshold:
                    result.append({
                        "position": i,
                        "change": float(d)
                    })

            return result
        except Exception as e:
            logger.error("Change point detection failed: %s", e)
            raise AnalysisError(f"Change point detection failed: {e}") from e