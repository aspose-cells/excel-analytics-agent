import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from app.logger import logger
from app.exceptions import AnalysisError


class ForecastingAnalysis:
    """Forecast future values using exponential smoothing."""

    @staticmethod
    def forecast(values: list[float], steps: int = 5) -> list[float]:
        """Forecast future data points using Holt-Winters Exponential Smoothing.

        Args:
            values: List of numeric values to base the forecast on.
            steps: Number of future steps to forecast (default 5).

        Returns:
            List of forecasted values.

        Raises:
            AnalysisError: If forecasting fails.
        """
        try:
            arr = np.array(values, dtype=float)

            model = ExponentialSmoothing(arr)
            fit = model.fit()

            forecast = fit.forecast(steps)

            return forecast.tolist()
        except Exception as e:
            logger.error("Forecasting failed: %s", e)
            raise AnalysisError(f"Forecasting failed: {e}") from e