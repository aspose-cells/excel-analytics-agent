import numpy as np
from scipy import stats
from app.logger import logger
from app.exceptions import AnalysisError


class HypothesisAnalysis:
    """Perform hypothesis testing (t-test, chi-square, ANOVA)."""

    @staticmethod
    def t_test_ind(
        group_a: list[float],
        group_b: list[float],
        equal_var: bool = False
    ) -> dict:
        """Independent two-sample t-test (Welch's by default).

        Args:
            group_a: First group of numeric values.
            group_b: Second group of numeric values.
            equal_var: If True, use Student's t-test (assume equal variance).

        Returns:
            Dict with keys: statistic, p_value, significant (p < 0.05),
            group_a_mean, group_b_mean, test_type.

        Raises:
            AnalysisError: If t-test fails.
        """
        try:
            a = np.array(group_a, dtype=float)
            b = np.array(group_b, dtype=float)

            statistic, p_value = stats.ttest_ind(a, b, equal_var=equal_var)

            return {
                "statistic": float(statistic),
                "p_value": float(p_value),
                "significant": p_value < 0.05,
                "group_a_mean": float(np.mean(a)),
                "group_b_mean": float(np.mean(b)),
                "test_type": "t_test_ind"
            }
        except Exception as e:
            logger.error("Independent t-test failed: %s", e)
            raise AnalysisError(f"Independent t-test failed: {e}") from e

    @staticmethod
    def t_test_paired(
        before: list[float],
        after: list[float]
    ) -> dict:
        """Paired t-test for before/after measurements.

        Args:
            before: Values before treatment.
            after: Values after treatment.

        Returns:
            Dict with keys: statistic, p_value, significant, mean_diff, test_type.

        Raises:
            AnalysisError: If paired t-test fails.
        """
        try:
            a = np.array(before, dtype=float)
            b = np.array(after, dtype=float)

            if len(a) != len(b):
                raise ValueError("Before and after must have same length")

            statistic, p_value = stats.ttest_rel(a, b)

            return {
                "statistic": float(statistic),
                "p_value": float(p_value),
                "significant": p_value < 0.05,
                "mean_diff": float(np.mean(b - a)),
                "test_type": "t_test_paired"
            }
        except Exception as e:
            logger.error("Paired t-test failed: %s", e)
            raise AnalysisError(f"Paired t-test failed: {e}") from e

    @staticmethod
    def chi_square(observed: list[list[int]]) -> dict:
        """Chi-square test of independence.

        Args:
            observed: Contingency table as list of lists (rows x cols).

        Returns:
            Dict with keys: statistic, p_value, significant, dof, expected, test_type.

        Raises:
            AnalysisError: If chi-square test fails.
        """
        try:
            observed_arr = np.array(observed, dtype=int)

            if observed_arr.ndim != 2:
                raise ValueError("Observed must be a 2D contingency table")

            statistic, p_value, dof, expected = stats.chi2_contingency(observed_arr)

            return {
                "statistic": float(statistic),
                "p_value": float(p_value),
                "significant": p_value < 0.05,
                "dof": int(dof),
                "expected": expected.tolist(),
                "test_type": "chi_square"
            }
        except Exception as e:
            logger.error("Chi-square test failed: %s", e)
            raise AnalysisError(f"Chi-square test failed: {e}") from e

    @staticmethod
    def anova(*groups: list[float]) -> dict:
        """One-way ANOVA test.

        Args:
            *groups: Two or more groups of numeric values.

        Returns:
            Dict with keys: statistic, p_value, significant,
            group_means, test_type.

        Raises:
            AnalysisError: If ANOVA fails.
        """
        try:
            if len(groups) < 2:
                raise ValueError("Need at least 2 groups for ANOVA")

            arrays = [np.array(g, dtype=float) for g in groups]
            statistic, p_value = stats.f_oneway(*arrays)

            return {
                "statistic": float(statistic),
                "p_value": float(p_value),
                "significant": p_value < 0.05,
                "group_means": [float(np.mean(a)) for a in arrays],
                "test_type": "anova"
            }
        except Exception as e:
            logger.error("ANOVA failed: %s", e)
            raise AnalysisError(f"ANOVA failed: {e}") from e
