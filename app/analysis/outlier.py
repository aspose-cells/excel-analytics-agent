import numpy as np
from app.logger import logger
from app.exceptions import AnalysisError


class OutlierAnalysis:
    """Detect outliers in data using the IQR method."""

    @staticmethod
    def iqr_outliers(values: list[float]) -> list[dict]:
        """Detect outliers using the Interquartile Range (IQR) method.

        Args:
            values: List of numeric values to analyze.

        Returns:
            List of dicts with keys: index, value for each outlier.

        Raises:
            AnalysisError: If outlier detection fails.
        """
        try:
            arr = np.array(values, dtype=float)

            q1 = np.percentile(arr, 25)
            q3 = np.percentile(arr, 75)

            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            result = []

            for i, v in enumerate(arr):
                if v < lower or v > upper:
                    result.append({
                        "index": i,
                        "value": float(v)
                    })

            return result
        except Exception as e:
            logger.error("Outlier detection failed: %s", e)
            raise AnalysisError(f"Outlier detection failed: {e}") from e