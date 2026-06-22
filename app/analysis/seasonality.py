from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd
from app.logger import logger
from app.exceptions import AnalysisError


class SeasonalityAnalysis:
    """Decompose time series into trend, seasonal, and residual components."""

    @staticmethod
    def analyze(values: list[float]) -> dict:
        """Decompose the time series using additive seasonal decomposition.

        Args:
            values: List of numeric time series values.

        Returns:
            Dict with keys: trend, seasonal, residual (each a list).

        Raises:
            AnalysisError: If seasonal decomposition fails.
        """
        try:
            series = pd.Series(values)

            result = seasonal_decompose(series, period=4, model='additive')

            return {
                "trend": result.trend.tolist(),
                "seasonal": result.seasonal.tolist(),
                "residual": result.resid.tolist()
            }
        except Exception as e:
            logger.error("Seasonality analysis failed: %s", e)
            raise AnalysisError(f"Seasonality analysis failed: {e}") from e