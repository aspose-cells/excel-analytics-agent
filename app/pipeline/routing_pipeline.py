from app.logger import logger
from app.exceptions import PipelineError
from app.llm.planner import Planner
from typing import Any, Dict


class RoutingPipeline:
    """Pipeline that routes user requests to the LLM planner."""

    def __init__(self) -> None:
        self.planner = Planner()

    def route(self, file_path: str, request: str) -> tuple[Dict[str, Any], int]:
        """Route a user request to the planner and return a plan with token usage.

        Args:
            file_path: Path to the Excel file.
            request: User's natural language request.

        Returns:
            Tuple of (plan dict, token usage count).
        """
        try:
            return self.planner.create_plan(request)
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            raise PipelineError(f"Routing failed: {e}") from e