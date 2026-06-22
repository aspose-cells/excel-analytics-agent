import json
import time
from pathlib import Path
from typing import Any

from app.logger import logger


class SessionState:
    def __init__(self, state_dir: str | Path = "output/sessions"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, Any] = {}

    def save(self, session_id: str, data: dict) -> Path:
        entry = {
            "session_id": session_id,
            "timestamp": time.time(),
            "data": data,
        }
        path = self.state_dir / f"{session_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)
        self._cache[session_id] = entry
        logger.info("Session %s saved to %s", session_id, path)
        return path

    def load(self, session_id: str) -> dict | None:
        if session_id in self._cache:
            return self._cache[session_id]
        path = self.state_dir / f"{session_id}.json"
        if not path.exists():
            return None
        with open(path, encoding="utf-8") as f:
            entry = json.load(f)
        self._cache[session_id] = entry
        return entry

    def list_sessions(self) -> list[str]:
        return [p.stem for p in self.state_dir.glob("*.json")]

    def clear_cache(self):
        self._cache.clear()
