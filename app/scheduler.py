import time
import threading
from typing import Callable

from app.logger import logger


class Scheduler:
    def __init__(self):
        self._tasks: list[dict] = []
        self._running = False
        self._thread: threading.Thread | None = None

    def add_task(self, name: str, fn: Callable, interval_seconds: float):
        self._tasks.append({
            "name": name,
            "fn": fn,
            "interval": interval_seconds,
            "last_run": 0.0,
        })
        logger.info("Scheduled task '%s' every %.1fs", name, interval_seconds)

    def _loop(self):
        while self._running:
            now = time.time()
            for task in self._tasks:
                if now - task["last_run"] >= task["interval"]:
                    try:
                        task["fn"]()
                        task["last_run"] = now
                        logger.debug("Scheduled task '%s' executed", task["name"])
                    except Exception as e:
                        logger.error("Scheduled task '%s' failed: %s", task["name"], e)
            time.sleep(1)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info("Scheduler started with %d tasks", len(self._tasks))

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Scheduler stopped")
