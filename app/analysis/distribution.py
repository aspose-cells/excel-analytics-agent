import numpy as np
from scipy.stats import normaltest
from app.logger import logger
from app.exceptions import AnalysisError


class DistributionAnalysis:
    """Analyze the distribution of data, including normality testing."""

    @staticmethod
    def check_normal_distribution(values: list[float]) -> dict:
        """Check if the data follows a normal distribution using D'Agostino-Pearson test.

        Args:
            values: List of numeric values to test.

        Returns:
            Dict with keys: statistic, pvalue, is_normal (True if p > 0.05).

        Raises:
            AnalysisError: If normality test fails.
        """
        try:
            arr = np.array(values, dtype=float)

            stat, p = normaltest(arr)

            return {
                "statistic": float(stat),
                "pvalue": float(p),
                "is_normal": p > 0.05
            }
        except Exception as e:
            logger.error("Normality test failed: %s", e)
            raise AnalysisError(f"Normality test failed: {e}") from e