import pytest
from app.analysis.regression import RegressionAnalysis
from app.exceptions import AnalysisError


def test_regression():

    values = [1, 2, 3, 4, 5]

    result = RegressionAnalysis.linear_regression(values)

    assert result["slope"] > 0


def test_polynomial_regression_parabola():

    values = [float(i * i) for i in range(10)]

    result = RegressionAnalysis.polynomial_regression(values, degree=2)

    assert result["degree"] == 2
    assert result["r_squared"] > 0.99
    assert len(result["coefficients"]) == 3


def test_polynomial_regression_better_than_linear_for_curved_data():

    values = [1, 3, 6, 9, 11, 12, 11, 9, 6, 3]

    result = RegressionAnalysis.polynomial_regression(values, degree=2)

    assert result["is_better_than_linear"] is True
    assert result["r_squared"] > 0.9


def test_polynomial_regression_linear_data_prefers_linear():

    values = [float(i) for i in range(10)]

    result = RegressionAnalysis.polynomial_regression(values, degree=2)

    assert result["is_better_than_linear"] is False


def test_polynomial_regression_degree_validation():

    with pytest.raises(AnalysisError):
        RegressionAnalysis.polynomial_regression([1.0, 2.0, 3.0], degree=1)


def test_polynomial_regression_clamps_degree_for_small_data():

    values = [1.0, 2.0, 3.0]

    result = RegressionAnalysis.polynomial_regression(values, degree=5)

    assert result["degree"] <= len(values) - 1


def test_polynomial_regression_clamps_degree_to_max():

    values = [float(i) for i in range(20)]

    result = RegressionAnalysis.polynomial_regression(values, degree=10)

    assert result["degree"] == 4
