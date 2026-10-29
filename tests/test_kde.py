import numpy as np
import pytest

from app.analysis.kde import KDEAnalysis
from app.exceptions import AnalysisError


def test_kde_detects_two_modes():
    np.random.seed(0)
    values = np.concatenate([
        np.random.normal(100, 15, 300),
        np.random.normal(800, 20, 300),
    ]).tolist()

    result = KDEAnalysis.estimate_density(values)

    assert result["n_modes"] == 2
    assert result["is_multimodal"] is True

    locations = sorted(result["mode_locations"])
    assert 60 < locations[0] < 140
    assert 740 < locations[1] < 860


def test_kde_detects_single_mode():
    np.random.seed(0)
    values = np.random.normal(50, 5, 500).tolist()

    result = KDEAnalysis.estimate_density(values)

    assert result["n_modes"] == 1
    assert result["is_multimodal"] is False


def test_kde_reports_bandwidth():
    np.random.seed(0)
    values = np.random.normal(0, 1, 200).tolist()

    result = KDEAnalysis.estimate_density(values)

    assert result["bandwidth"] > 0


def test_kde_requires_min_points():
    with pytest.raises(AnalysisError):
        KDEAnalysis.estimate_density([1.0, 2.0, 3.0])


def test_kde_rejects_constant_data():
    with pytest.raises(AnalysisError):
        KDEAnalysis.estimate_density([5.0] * 50)


def test_kde_ignores_non_finite_values():
    np.random.seed(0)
    values = np.random.normal(10, 1, 100).tolist()
    values = [float("nan"), float("inf")] + values

    result = KDEAnalysis.estimate_density(values)

    assert result["n_modes"] >= 1
