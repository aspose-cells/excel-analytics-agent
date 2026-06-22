"""Analysis module for Excel AI Agent.

Provides statistical, trend, anomaly, and other data analysis tools.
"""

from app.logger import logger

from .anomaly import AnomalyAnalysis
from .change_point import ChangePointAnalysis
from .clustering import ClusteringAnalysis
from .correlation import CorrelationAnalysis
from .distribution import DistributionAnalysis
from .fft_analysis import FFTAnalysis
from .forecasting import ForecastingAnalysis
from .outlier import OutlierAnalysis
from .pca_analysis import PCAAnalysis
from .regression import RegressionAnalysis
from .seasonality import SeasonalityAnalysis
from .smoothing import SmoothingAnalysis
from .statistics_analysis import StatisticsAnalysis
from .trend import TrendAnalysis

__all__ = [
    "AnomalyAnalysis",
    "ChangePointAnalysis",
    "ClusteringAnalysis",
    "CorrelationAnalysis",
    "DistributionAnalysis",
    "FFTAnalysis",
    "ForecastingAnalysis",
    "OutlierAnalysis",
    "PCAAnalysis",
    "RegressionAnalysis",
    "SeasonalityAnalysis",
    "SmoothingAnalysis",
    "StatisticsAnalysis",
    "TrendAnalysis",
]
