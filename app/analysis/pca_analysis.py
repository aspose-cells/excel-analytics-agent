from sklearn.decomposition import PCA
import pandas as pd
from app.logger import logger
from app.exceptions import AnalysisError


class PCAAnalysis:
    """Perform Principal Component Analysis on DataFrame data."""

    @staticmethod
    def analyze(df: pd.DataFrame) -> dict:
        """Reduce data to 2 principal components and return explained variance.

        Args:
            df: Input DataFrame with numeric columns.

        Returns:
            Dict with keys: explained_variance (list), components (list),
            rows_used (int, rows remaining after dropping missing values).

        Raises:
            AnalysisError: If PCA analysis fails.
        """
        try:
            numeric = df.select_dtypes(include=['number'])

            # sklearn cannot handle missing values; use complete rows only.
            numeric = numeric.dropna()

            n_features = numeric.shape[1]
            n_components = min(2, n_features)

            if n_components < 1 or len(numeric) < 2:
                return {
                    "explained_variance": [],
                    "components": [],
                    "rows_used": int(len(numeric)),
                }

            pca = PCA(n_components=n_components)

            components = pca.fit_transform(numeric)

            return {
                "explained_variance": pca.explained_variance_ratio_.tolist(),
                "components": components.tolist(),
                "rows_used": int(len(numeric)),
            }
        except Exception as e:
            logger.error("PCA analysis failed: %s", e)
            raise AnalysisError(f"PCA analysis failed: {e}") from e