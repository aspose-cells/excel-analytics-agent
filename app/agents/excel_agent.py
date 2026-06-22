from app.logger import logger
from app.exceptions import ExcelAgentError
from app.pipeline.routing_pipeline import RoutingPipeline
from app.pipeline.execution_pipeline import ExecutionPipeline
from app.pipeline.report_pipeline import ReportPipeline
from typing import Any, Dict


class ExcelAgent:
    """Main agent that orchestrates routing, execution, and reporting."""

    def __init__(self) -> None:
        self.router = RoutingPipeline()
        self.executor = ExecutionPipeline()
        self.reporter = ReportPipeline()

    def run(self, file_path: str, output_file: str, user_request: str) -> Dict[str, Any]:
        """Execute the full analysis workflow: plan, execute, and generate report.

        Args:
            file_path: Path to the input Excel file.
            output_file: Path for the output report.
            user_request: User's natural language request.

        Returns:
            Dict containing the analysis results.

        Raises:
            ExcelAgentError: If any stage of the workflow fails.
        """
        logger.info("Reading and planning...")

        try:
            plan = self.router.route(
                file_path=file_path,
                request=user_request
            )
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            raise ExcelAgentError(f"Routing failed: {e}") from e

        logger.info(f"Plan: {plan}")

        try:
            results = self.executor.execute(
                file_path=file_path,
                plan=plan
            )
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            raise ExcelAgentError(f"Execution failed: {e}") from e

        try:
            self.reporter.generate(results, output_file)
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise ExcelAgentError(f"Report generation failed: {e}") from e

        return results