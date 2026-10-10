from app.logger import logger
from app.exceptions import ToolNotFoundError
from app.analysis.hypothesis import HypothesisAnalysis
from typing import Any, Dict, List


def run_hypothesis(values: List[float]) -> Dict[str, Any]:
    """Run hypothesis tests on a list of values.

    For series input: automatically selects the best test.
    - 2 groups -> Welch's t-test
    - 3+ groups -> ANOVA

    Args:
        values: List of numeric values to analyze.

    Returns:
        Dict containing hypothesis test results.
    """
    try:
        if len(values) < 2:
            raise ValueError("Need at least 2 columns for hypothesis testing")
        elif len(values) == 2:
            return HypothesisAnalysis.t_test_ind(values[0], values[1])
        else:
            return HypothesisAnalysis.anova(*values)
    except Exception as e:
        logger.error(f"Hypothesis testing failed: {e}")
        raise ToolNotFoundError(f"Hypothesis testing failed: {e}") from e


def register() -> Dict[str, Any]:
    """Register the hypothesis testing tool in the tool registry.

    Returns:
        Dict describing the tool's function and input type.
    """
    return {
        "hypothesis": {
            "func": run_hypothesis,
            "input": "series"
        }
    }
