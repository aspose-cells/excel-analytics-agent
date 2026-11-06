from typing import Any, Dict

import pandas as pd

from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.data_profile import DataQualityAnalysis


def run_data_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """Profile the data quality of a DataFrame.

    Args:
        df: The full table to inspect, including text columns.

    Returns:
        Dict containing table statistics, per-column profiles, issues
        and a quality score.
    """
    try:
        return DataQualityAnalysis.profile(df)
    except Exception as e:
        logger.error(f"Data quality profiling failed: {e}")
        raise ToolNotFoundError(
            f"Data quality profiling failed: {e}"
        ) from e


def register() -> Dict[str, Any]:
    """Register the data quality tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "data_profile": {
            "func": run_data_profile,
            "input": "dataframe"
        }
    }
