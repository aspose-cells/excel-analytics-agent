import json
import os
import time
import urllib.request
import urllib.error
from typing import Any
from uuid import uuid4

from app.logger import logger

METRICS_API_URL = "https://metrics-api.aspose.app/agents"
METRICS_API_KEY = os.getenv("METRICS_API_KEY", "")


def send_agent_metrics(
    agent_name: str,
    agent_owner: str,
    job_type: str,
    status: str,
    items_discovered: int = 0,
    items_failed: int = 0,
    items_succeeded: int = 0,
    run_duration_ms: float = 0.0,
    token_usage: int = 0,
    api_calls_count: int = 0,
    run_id: str | None = None,
    product: str = "Aspose.Cells",
    platform: str = "Python",
    website: str = "aspose.com",
    website_section: str = "docs",
    item_name: str = "excel_analysis",
) -> dict[str, Any]:
    if not METRICS_API_KEY:
        logger.warning("METRICS_API_KEY not set, skipping metrics report")
        return {"error": "METRICS_API_KEY not set"}

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + "+00:00"

    payload = {
        "timestamp": timestamp,
        "agent_name": agent_name,
        "agent_owner": agent_owner,
        "job_type": job_type,
        "run_id": run_id or f"run_{uuid4().hex[:12]}",
        "status": status,
        "product": product,
        "platform": platform,
        "website": website,
        "website_section": website_section,
        "item_name": item_name,
        "items_discovered": items_discovered,
        "items_failed": items_failed,
        "items_succeeded": items_succeeded,
        "run_duration_ms": run_duration_ms,
        "token_usage": token_usage,
        "api_calls_count": api_calls_count,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        METRICS_API_URL,
        data=data,
        method="PUT",
        headers={
            "Content-Type": "application/json",
            "X-Api-Key": METRICS_API_KEY,
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            logger.info("Metrics reported: status=%s, run_id=%s", status, payload["run_id"])
            return json.loads(body) if body else {"status": "ok"}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        logger.error("Metrics API HTTP %d: %s", e.code, error_body)
        return {"error": f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        logger.error("Metrics API request failed: %s", e)
        return {"error": str(e)}
