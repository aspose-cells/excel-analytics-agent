import numpy as np
from scipy.fft import fft
from app.logger import logger
from app.exceptions import AnalysisError


class FFTAnalysis:
    """Perform Fast Fourier Transform analysis on time series data."""

    @staticmethod
    def analyze(values: list[float]) -> list[float]:
        """Compute the magnitude spectrum using FFT.

        Args:
            values: List of numeric values to analyze.

        Returns:
            List of FFT magnitude values.

        Raises:
            AnalysisError: If FFT analysis fails.
        """
        try:
            arr = np.array(values, dtype=float)

            spectrum = fft(arr)

            magnitude = np.abs(spectrum)

            return magnitude.tolist()
        except Exception as e:
            logger.error("FFT analysis failed: %s", e)
            raise AnalysisError(f"FFT analysis failed: {e}") from e