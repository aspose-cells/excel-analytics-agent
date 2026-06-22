import numpy as np
from scipy.signal import savgol_filter
from scipy.stats import linregress
from app.logger import logger
from app.exceptions import AnalysisError


class TrendAnalysis:
    """Analyze and smooth trends in time series data."""

    @staticmethod
    def smooth(values: list[float]) -> list[float]:
        """Apply Savitzky-Golay smoothing to the input values.

        Args:
            values: List of numeric values to smooth.

        Returns:
            List of smoothed values (or original list if fewer than 5 points).

        Raises:
            AnalysisError: If smoothing fails.
        """
        try:
            arr = np.array(values, dtype=float)

            if len(arr) < 5:
                return arr.tolist()

            smoothed = savgol_filter(arr, 5, 2)
            return smoothed.tolist()
        except Exception as e:
            logger.error("Trend smoothing failed: %s", e)
            raise AnalysisError(f"Trend smoothing failed: {e}") from e

    @staticmethod
    def analyze(values: list[float]) -> dict:
        """Perform a full trend analysis including slope and smoothing.

        Args:
            values: List of numeric values to analyze.

        Returns:
            Dict with keys: slope (float), smoothed (list of floats).

        Raises:
            AnalysisError: If trend analysis fails.
        """
        try:
            arr = np.array(values, dtype=float)

            x = np.arange(len(arr))
            slope, _, _, _, _ = linregress(x, arr)

            if len(arr) < 5:
                smoothed = arr.tolist()
            else:
                smoothed = savgol_filter(arr, 5, 2).tolist()

            return {
                "slope": float(slope),
                "smoothed": smoothed
            }
        except Exception as e:
            logger.error("Trend analysis failed: %s", e)
            raise AnalysisError(f"Trend analysis failed: {e}") from e