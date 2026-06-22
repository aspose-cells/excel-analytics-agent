import pandas as pd
from app.logger import logger
from app.exceptions import AnalysisError


class CorrelationAnalysis:
    """Compute correlation matrices for DataFrame columns."""

    @staticmethod
    def correlation_matrix(df: pd.DataFrame) -> dict:
        """Compute the pairwise correlation matrix of numeric columns.

        Args:
            df: Input DataFrame with numeric columns.

        Returns:
            Dict representation of the correlation matrix.

        Raises:
            AnalysisError: If correlation computation fails.
        """
        try:
            numeric_df = df.select_dtypes(include=['number'])

            return numeric_df.corr().to_dict()
        except Exception as e:
            logger.error("Correlation analysis failed: %s", e)
            raise AnalysisError(f"Correlation analysis failed: {e}") from e