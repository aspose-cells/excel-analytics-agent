import numpy as np
from app.analysis.hypothesis import HypothesisAnalysis


def test_t_test_ind_detects_difference():
    np.random.seed(42)
    group_a = np.random.normal(10, 1, 100).tolist()
    group_b = np.random.normal(15, 1, 100).tolist()
    result = HypothesisAnalysis.t_test_ind(group_a, group_b)
    assert result["p_value"] < 0.05
    assert result["significant"] == True
    assert result["test_type"] == "t_test_ind"


def test_t_test_ind_no_difference():
    np.random.seed(42)
    group_a = np.random.normal(10, 1, 100).tolist()
    group_b = np.random.normal(10, 1, 100).tolist()
    result = HypothesisAnalysis.t_test_ind(group_a, group_b)
    assert result["p_value"] > 0.05
    assert result["significant"] == False


def test_t_test_paired():
    np.random.seed(42)
    before = np.random.normal(10, 1, 50).tolist()
    after = [x + 2 for x in before]
    result = HypothesisAnalysis.t_test_paired(before, after)
    assert result["p_value"] < 0.05
    assert result["significant"] == True
    assert result["test_type"] == "t_test_paired"


def test_t_test_paired_length_mismatch():
    before = [1.0, 2.0, 3.0]
    after = [1.0, 2.0]
    try:
        HypothesisAnalysis.t_test_paired(before, after)
        assert False, "Should have raised AnalysisError"
    except Exception as e:
        assert "same length" in str(e)


def test_chi_square():
    observed = [[30, 10], [10, 30]]
    result = HypothesisAnalysis.chi_square(observed)
    assert result["p_value"] < 0.05
    assert result["significant"] == True
    assert result["test_type"] == "chi_square"
    assert result["dof"] == 1


def test_chi_square_no_association():
    observed = [[25, 25], [25, 25]]
    result = HypothesisAnalysis.chi_square(observed)
    assert result["p_value"] > 0.05
    assert result["significant"] == False


def test_anova_multiple_groups():
    np.random.seed(42)
    g1 = np.random.normal(10, 1, 50).tolist()
    g2 = np.random.normal(12, 1, 50).tolist()
    g3 = np.random.normal(14, 1, 50).tolist()
    result = HypothesisAnalysis.anova(g1, g2, g3)
    assert result["p_value"] < 0.05
    assert result["significant"] == True
    assert result["test_type"] == "anova"
    assert len(result["group_means"]) == 3


def test_anova_no_difference():
    np.random.seed(42)
    g1 = np.random.normal(10, 1, 50).tolist()
    g2 = np.random.normal(10, 1, 50).tolist()
    result = HypothesisAnalysis.anova(g1, g2)
    assert result["p_value"] > 0.05
    assert result["significant"] == False


def test_anova_insufficient_groups():
    try:
        HypothesisAnalysis.anova([1.0, 2.0, 3.0])
        assert False, "Should have raised AnalysisError"
    except Exception as e:
        assert "at least 2 groups" in str(e)


def test_chi_square_invalid_input():
    try:
        HypothesisAnalysis.chi_square([1, 2, 3])
        assert False, "Should have raised AnalysisError"
    except Exception as e:
        assert "2D" in str(e)
