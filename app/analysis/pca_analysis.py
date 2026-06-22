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
            Dict with keys: explained_variance (list), components (list).

        Raises:
            AnalysisError: If PCA analysis fails.
        """
        try:
            numeric = df.select_dtypes(include=['number'])

            pca = PCA(n_components=2)

            components = pca.fit_transform(numeric)

            return {
                "explained_variance": pca.explained_variance_ratio_.tolist(),
                "components": components.tolist()
            }
        except Exception as e:
            logger.error("PCA analysis failed: %s", e)
            raise AnalysisError(f"PCA analysis failed: {e}") from e