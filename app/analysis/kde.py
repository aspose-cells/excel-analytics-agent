import numpy as np
from scipy.stats import gaussian_kde
from app.logger import logger
from app.exceptions import AnalysisError


class KDEAnalysis:
    """Estimate data density with KDE and detect distribution modes."""

    MIN_POINTS = 10

    @staticmethod
    def estimate_density(
        values: list[float],
        grid_points: int = 500,
        peak_ratio: float = 0.05,
    ) -> dict:
        """Estimate probability density (KDE) and detect its modes.

        A mode is a local maximum of the estimated density. Modes whose
        density is below ``peak_ratio`` of the global maximum are
        ignored, which filters trivial numerical bumps in the tails.

        Args:
            values: List of numeric values to analyze.
            grid_points: Number of points on the evaluation grid.
            peak_ratio: Minimum relative density (fraction of the
                global maximum) required for a local maximum to count
                as a mode (default 0.05 = 5%).

        Returns:
            Dict with keys: bandwidth (float), n_modes (int),
            mode_locations (list[float]), is_multimodal (bool).

        Raises:
            AnalysisError: If there are too few finite values, the data
                is constant, or estimation fails.
        """
        try:
            arr = np.asarray(values, dtype=float)
            arr = arr[np.isfinite(arr)]

            if arr.size < KDEAnalysis.MIN_POINTS:
                raise AnalysisError(
                    f"KDE requires at least {KDEAnalysis.MIN_POINTS} "
                    f"finite values, got {arr.size}"
                )

            std = float(np.std(arr))
            if std == 0.0:
                raise AnalysisError("KDE requires non-constant data")

            kde = gaussian_kde(arr)

            x_grid = np.linspace(
                float(arr.min()), float(arr.max()), grid_points
            )
            density = kde(x_grid)

            threshold = float(density.max()) * peak_ratio
            mode_indices = [
                i
                for i in range(1, len(density) - 1)
                if density[i] > density[i - 1]
                and density[i] > density[i + 1]
                and density[i] >= threshold
            ]

            return {
                "bandwidth": float(kde.factor * std),
                "n_modes": len(mode_indices),
                "mode_locations": [float(x_grid[i]) for i in mode_indices],
                "is_multimodal": len(mode_indices) > 1,
            }
        except AnalysisError:
            raise
        except Exception as e:
            logger.error("KDE analysis failed: %s", e)
            raise AnalysisError(f"KDE analysis failed: {e}") from e
