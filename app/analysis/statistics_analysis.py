import numpy as np
from scipy.stats import skew, kurtosis
from app.logger import logger
from app.exceptions import AnalysisError


class StatisticsAnalysis:
    """Compute descriptive statistics for a dataset."""

    @staticmethod
    def describe(values: list[float]) -> dict:
        """Compute descriptive statistics (mean, median, std, variance, etc.).

        Args:
            values: List of numeric values to describe.

        Returns:
            Dict with keys: mean, median, std, variance, min, max,
            skewness, kurtosis.

        Raises:
            AnalysisError: If statistics computation fails.
        """
        try:
            arr = np.array(values, dtype=float)

            return {
                "mean": float(np.mean(arr)),
                "median": float(np.median(arr)),
                "std": float(np.std(arr)),
                "variance": float(np.var(arr)),
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
                "skewness": float(skew(arr)),
                "kurtosis": float(kurtosis(arr))
            }
        except Exception as e:
            logger.error("Statistics description failed: %s", e)
            raise AnalysisError(f"Statistics description failed: {e}") from e