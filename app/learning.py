import json
import time
import os
from pathlib import Path
from typing import Any

from app.logger import logger
from app.state import SessionState


class LearningEngine:
    def __init__(self, history_dir: str | Path = "output/learning"):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.state = SessionState(str(self.history_dir / "sessions"))
        self._load_history()

    def _load_history(self):
        self.history: list[dict] = []
        for f in sorted(self.history_dir.glob("execution_*.json")):
            try:
                with open(f) as fp:
                    self.history.append(json.load(fp))
            except Exception:
                pass
        logger.info("LearningEngine loaded %d past executions", len(self.history))

    def record_execution(
        self,
        request: str,
        tools_used: list[str],
        success: bool,
        duration: float,
        error: str | None = None,
    ):
        entry = {
            "timestamp": time.time(),
            "request": request,
            "tools_used": tools_used,
            "success": success,
            "duration": duration,
            "error": error,
        }
        path = self.history_dir / f"execution_{int(time.time())}.json"
        with open(path, "w") as f:
            json.dump(entry, f, indent=2)
        self.history.append(entry)
        logger.info("Recorded execution: success=%s, tools=%s", success, tools_used)

    def get_tool_success_rates(self) -> dict[str, float]:
        rates: dict[str, dict] = {}
        for entry in self.history:
            for tool in entry.get("tools_used", []):
                if tool not in rates:
                    rates[tool] = {"ok": 0, "total": 0}
                rates[tool]["total"] += 1
                if entry.get("success"):
                    rates[tool]["ok"] += 1
        return {
            tool: (v["ok"] / max(v["total"], 1)) * 100
            for tool, v in rates.items()
        }

    def get_recommended_tools(self, top_n: int = 5) -> list[str]:
        rates = self.get_tool_success_rates()
        sorted_tools = sorted(rates.items(), key=lambda x: -x[1])
        return [tool for tool, _ in sorted_tools[:top_n]]

    def get_metrics(self) -> dict:
        total = len(self.history)
        successes = sum(1 for e in self.history if e.get("success"))
        failures = total - successes
        avg_duration = (
            sum(e.get("duration", 0) for e in self.history) / max(total, 1)
        )
        return {
            "total_executions": total,
            "successes": successes,
            "failures": failures,
            "success_rate": (successes / max(total, 1)) * 100 if total > 0 else 0,
            "avg_duration": round(avg_duration, 3),
            "tool_success_rates": self.get_tool_success_rates(),
        }
