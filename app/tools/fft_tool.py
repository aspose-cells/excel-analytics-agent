from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.fft_analysis import FFTAnalysis
from typing import Any, Dict, List


def run_fft(values: List[float]) -> Dict[str, Any]:
    """Run FFT analysis on a list of values.

    Args:
        values: List of numeric values to analyze.

    Returns:
        Dict containing FFT analysis results.
    """
    try:
        return FFTAnalysis.analyze(values)
    except Exception as e:
        logger.error(f"FFT analysis failed: {e}")
        raise ToolNotFoundError(f"FFT analysis failed: {e}") from e

def register() -> Dict[str, Any]:
    """Register the FFT tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "fft": {
            "func": run_fft,
            "input": "series"
        }
    }