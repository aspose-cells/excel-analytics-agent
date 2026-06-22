import importlib
import time
from dataclasses import dataclass, field
from typing import Callable

from app.logger import logger


@dataclass
class HealthCheck:
    name: str
    check_fn: Callable[[], bool]
    critical: bool = False
    last_ok: bool | None = None
    last_checked: float = 0.0


class HealthRegistry:
    _checks: list[HealthCheck] = []

    @classmethod
    def register(cls, check: HealthCheck):
        cls._checks.append(check)
        logger.debug("Health check registered: %s", check.name)

    @classmethod
    def run_all(cls) -> dict:
        results = {}
        all_ok = True
        for check in cls._checks:
            try:
                ok = check.check_fn()
                check.last_ok = ok
                check.last_checked = time.time()
            except Exception:
                ok = False
                check.last_ok = False
            results[check.name] = {
                "ok": ok,
                "critical": check.critical,
            }
            if check.critical and not ok:
                all_ok = False
        results["overall"] = all_ok
        return results


def _check_dependencies() -> bool:
    required = ["openai", "numpy", "pandas", "aspose.cells"]
    for pkg in required:
        try:
            importlib.import_module(pkg)
        except ImportError:
            logger.error("Missing dependency: %s", pkg)
            return False
    return True


def _check_output_dir() -> bool:
    from pathlib import Path
    return Path("output").exists() and Path("samples").exists()


HealthRegistry.register(HealthCheck("dependencies", _check_dependencies, critical=True))
HealthRegistry.register(HealthCheck("directories", _check_output_dir, critical=False))
