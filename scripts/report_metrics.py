import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.metrics import send_agent_metrics


def main():
    parser = argparse.ArgumentParser(description="Report agent metrics to Aspose Metrics API")
    parser.add_argument("--agent-name", default="Excel AI Agent")
    parser.add_argument("--agent-owner", default="Xinya Zhu")
    parser.add_argument("--job-type", default="production")
    parser.add_argument("--status", default="success", choices=["success", "failure", "running"])
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--items-discovered", type=int, default=0)
    parser.add_argument("--items-failed", type=int, default=0)
    parser.add_argument("--items-succeeded", type=int, default=0)
    parser.add_argument("--run-duration-ms", type=float, default=0.0)
    parser.add_argument("--token-usage", type=int, default=0)
    parser.add_argument("--api-calls-count", type=int, default=0)
    parser.add_argument("--item-name", default="excel_analysis")
    args = parser.parse_args()

    result = send_agent_metrics(
        agent_name=args.agent_name,
        agent_owner=args.agent_owner,
        job_type=args.job_type,
        status=args.status,
        run_id=args.run_id,
        items_discovered=args.items_discovered,
        items_failed=args.items_failed,
        items_succeeded=args.items_succeeded,
        run_duration_ms=args.run_duration_ms,
        token_usage=args.token_usage,
        api_calls_count=args.api_calls_count,
        item_name=args.item_name,
    )

    if "error" in result:
        print(f"Error: {result['error']}")
        return 1

    print(f"Metrics reported successfully: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
