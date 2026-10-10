import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from app.logger import logger
from app.exceptions import AnalysisError


class ARIMAForecast:
    """Forecast future values using ARIMA (AutoRegressive Integrated Moving Average)."""

    @staticmethod
    def forecast(
        values: list[float],
        steps: int = 5,
        order: tuple[int, int, int] = (1, 1, 1)
    ) -> dict:
        """Forecast future data points using ARIMA.

        Args:
            values: List of numeric time series values.
            steps: Number of future steps to forecast (default 5).
            order: ARIMA order (p, d, q) where:
                p = AR order (number of lag observations)
                d = Degree of differencing
                q = MA order (size of moving average window)

        Returns:
            Dict with keys: forecast (list of predicted values),
            order (p, d, q tuple), aic (model fit metric),
            steps (number of forecasted points).

        Raises:
            AnalysisError: If ARIMA forecasting fails.
        """
        try:
            arr = np.array(values, dtype=float)

            if len(arr) < 10:
                raise AnalysisError(
                    "Insufficient data for ARIMA: need at least 10 points"
                )

            model = ARIMA(arr, order=order)
            fit = model.fit()

            predicted = fit.forecast(steps)

            return {
                "forecast": predicted.tolist(),
                "order": list(order),
                "aic": float(fit.aic),
                "steps": steps
            }
        except AnalysisError:
            raise
        except Exception as e:
            logger.error("ARIMA forecasting failed: %s", e)
            raise AnalysisError(f"ARIMA forecasting failed: {e}") from e
