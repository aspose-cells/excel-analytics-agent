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

    @staticmethod
    def polynomial_regression(values: list[float], degree: int = 2) -> dict:
        """Fit a polynomial regression model of the given degree.

        Args:
            values: List of numeric y-values; x is auto-generated as 0..N-1.
            degree: Polynomial degree (default 2, i.e. quadratic/parabola).
                Clamped to 4 (upper bound for numerical stability) and
                lowered automatically when there are fewer data points
                than ``degree + 1``.

        Returns:
            Dict with keys: coefficients (list, highest degree first,
            same order as ``numpy.polyfit``), r_squared (float, 1.0 =
            perfect fit), degree (int, actual degree used after
            clamping), is_better_than_linear (bool, True when the
            polynomial R-squared exceeds the linear R-squared by at
            least 0.01).

        Raises:
            AnalysisError: If degree < 2 or the fit fails.
        """
        try:
            if degree < 2:
                raise AnalysisError(
                    "Polynomial degree must be >= 2 "
                    "(use linear_regression for degree 1)"
                )

            MAX_DEGREE = 4
            if degree > MAX_DEGREE:
                logger.warning(
                    "Polynomial degree %s clamped to %s for numerical stability",
                    degree,
                    MAX_DEGREE,
                )
                degree = MAX_DEGREE

            arr = np.array(values, dtype=float)
            if arr.size == 0:
                raise AnalysisError("Cannot fit polynomial regression to empty data")

            if arr.size < degree + 1:
                degree = max(1, arr.size - 1)
                if degree < 2:
                    raise AnalysisError(
                        "Not enough data points for polynomial regression "
                        "(need at least 3)"
                    )

            x = np.arange(arr.size)

            coefficients = np.polyfit(x, arr, degree)

            y_pred = np.polyval(coefficients, x)
            ss_res = float(np.sum((arr - y_pred) ** 2))
            ss_tot = float(np.sum((arr - np.mean(arr)) ** 2))

            if ss_tot == 0:
                r_squared = 1.0 if ss_res == 0 else 0.0
                linear_r2 = 1.0
            else:
                r_squared = 1 - (ss_res / ss_tot)

                linear_coefficients = np.polyfit(x, arr, 1)
                linear_pred = np.polyval(linear_coefficients, x)
                linear_r2 = 1 - (
                    float(np.sum((arr - linear_pred) ** 2)) / ss_tot
                )

            return {
                "coefficients": [float(c) for c in coefficients],
                "r_squared": float(r_squared),
                "degree": int(degree),
                "is_better_than_linear": bool(r_squared - linear_r2 >= 0.01),
            }
        except AnalysisError:
            raise
        except Exception as e:
            logger.error("Polynomial regression failed: %s", e)
            raise AnalysisError(f"Polynomial regression failed: {e}") from e