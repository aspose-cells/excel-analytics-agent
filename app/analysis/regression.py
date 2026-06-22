import numpy as np
from scipy.stats import linregress
from app.logger import logger
from app.exceptions import AnalysisError


class RegressionAnalysis:
    """Perform linear regression analysis on data."""

    @staticmethod
    def linear_regression(values: list[float]) -> dict:
        """Fit a linear regression model (y = slope * x + intercept).

        Args:
            values: List of numeric y-values; x is auto-generated as 0..N-1.

        Returns:
            Dict with keys: slope, intercept, rvalue, pvalue, stderr.

        Raises:
            AnalysisError: If regression fails.
        """
        try:
            x = np.arange(len(values))
            y = np.array(values, dtype=float)

            result = linregress(x, y)

            return {
                "slope": result.slope,
                "intercept": result.intercept,
                "rvalue": result.rvalue,
                "pvalue": result.pvalue,
                "stderr": result.stderr
            }
        except Exception as e:
            logger.error("Linear regression failed: %s", e)
            raise AnalysisError(f"Linear regression failed: {e}") from e