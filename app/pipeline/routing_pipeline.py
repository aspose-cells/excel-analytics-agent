from pathlib import Path

from app.logger import logger
from app.exceptions import PipelineError
from app.llm.planner import Planner
from app.excel.reader import ExcelReader
from app.excel.schema import build_schema_summary
from typing import Any, Dict


class RoutingPipeline:
    """Pipeline that routes user requests to the LLM planner."""

    def __init__(self) -> None:
        self.planner = Planner()

    def route(self, file_path: str, request: str) -> tuple[Dict[str, Any], int]:
        """Route a user request to the planner and return a plan with token usage.

        The input file is read (header/rows) to build a compact schema
        summary, which is sent to the planner so that tool and column
        selection can be grounded in the actual data. If the file cannot
        be read, planning continues without a schema.

        Args:
            file_path: Path to the Excel file.
            request: User's natural language request.

        Returns:
            Tuple of (plan dict, token usage count).
        """
        schema = None
        try:
            df = ExcelReader.load_sheet_as_dataframe(file_path)
            schema = build_schema_summary(
                df, file_name=Path(file_path).name
            )
        except Exception as e:
            logger.warning(
                f"Could not build data schema for '{file_path}', "
                f"planning without it: {e}"
            )

        try:
            return self.planner.create_plan(request, schema=schema)
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            raise PipelineError(f"Routing failed: {e}") from e
