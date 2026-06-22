"""
from app.tools.anomaly_tool import run_anomaly
from app.tools.trend_tool import run_trend
from app.tools.correlation_tool import run_correlation
from app.tools.pca_tool import run_pca

TOOL_REGISTRY = {
    "anomaly": {
        "func": run_anomaly,
        "input": "series"
    },

    "trend": {
        "func": run_trend,
        "input": "series"
    },

    "correlation": {
        "func": run_correlation,
        "input": "dataframe"
    },

    "pca": {
        "func": run_pca,
        "input": "dataframe"
    }
}

"""
import importlib
import pkgutil
import app.tools as tools
from app.logger import logger
from app.exceptions import ToolNotFoundError
from typing import Any, Dict

TOOL_REGISTRY: Dict[str, Any] = {}

for _, module_name, _ in pkgutil.iter_modules(tools.__path__):

    try:
        module = importlib.import_module(f"app.tools.{module_name}")

        if hasattr(module, "register"):
            TOOL_REGISTRY.update(module.register())
    except Exception as e:
        logger.error(f"Failed to load tool module {module_name}: {e}")
