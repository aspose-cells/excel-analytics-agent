import pandas as pd
from app.logger import logger
from app.exceptions import AnalysisError


class SmoothingAnalysis:
    """Smooth time series data using moving average."""

    @staticmethod
    def moving_average(values: list[float], window: int = 3) -> list[float]:
        """Apply a simple moving average to the input values.

        Args:
            values: List of numeric values to smooth.
            window: Rolling window size (default 3).

        Returns:
            List of smoothed values (NaN for initial window-1 positions).

        Raises:
            AnalysisError: If smoothing fails.
        """
        try:
            series = pd.Series(values)

            return series.rolling(window=window).mean().tolist()
        except Exception as e:
            logger.error("Moving average smoothing failed: %s", e)
            raise AnalysisError(f"Moving average smoothing failed: {e}") from e