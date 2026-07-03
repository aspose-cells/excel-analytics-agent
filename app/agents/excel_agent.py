import time
from typing import Any, Dict

from app.logger import logger
from app.exceptions import ExcelAgentError
from app.pipeline.routing_pipeline import RoutingPipeline
from app.pipeline.execution_pipeline import ExecutionPipeline
from app.pipeline.report_pipeline import ReportPipeline
from app.metrics import send_agent_metrics
from app.learning import LearningEngine


class ExcelAgent:
    """Main agent that orchestrates routing, execution, and reporting."""

    def __init__(self, agent_name: str = "Excel AI Agent",
                 agent_owner: str = "Xinya Zhu") -> None:
        self.router = RoutingPipeline()
        self.executor = ExecutionPipeline()
        self.reporter = ReportPipeline()
        self.agent_name = agent_name
        self.agent_owner = agent_owner
        self.learning = LearningEngine()

    def run(self, file_path: str, output_file: str, user_request: str,
            job_type: str = "production",
            output_excel: str | None = None) -> Dict[str, Any]:
        """Execute the full analysis workflow: plan, execute, and generate report.

        Args:
            file_path: Path to the input Excel file (read-only).
            output_file: Path for the output report.
            output_excel: Path for the output Excel file. Source data is
                copied here with all results. If None, defaults to
                ``output_file`` with ``.xlsx`` extension.
            user_request: User's natural language request.
            job_type: Type of job ('production' or 'test').

        Returns:
            Dict containing the analysis results.

        Raises:
            ExcelAgentError: If any stage of the workflow fails.
        """
        start_time = time.time()
        status = "success"
        error_msg: str | None = None
        tools_used: list[str] = []

        logger.info("Reading and planning...")

        try:
            plan, token_usage = self.router.route(
                file_path=file_path,
                request=user_request
            )
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            raise ExcelAgentError(f"Routing failed: {e}") from e

        logger.info(f"Plan: {plan}")

        tools_used = plan.get("tools", []) if isinstance(plan, dict) else []

        try:
            output_excel_path = output_excel or output_file.rsplit(".", 1)[0] + ".xlsx"
            results = self.executor.execute(
                file_path=file_path,
                plan=plan,
                output_path=output_excel_path
            )
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            status = "failure"
            error_msg = str(e)
            raise ExcelAgentError(f"Execution failed: {e}") from e

        try:
            self.reporter.generate(results, output_file)
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            status = "failure"
            error_msg = str(e)
            raise ExcelAgentError(f"Report generation failed: {e}") from e

        duration_ms = (time.time() - start_time) * 1000

        analysis_results = results.get("analysis_results", {})
        total_analyses = sum(
            len(cols) if isinstance(cols, dict) else 0
            for cols in analysis_results.values()
        )

        send_agent_metrics(
            agent_name=self.agent_name,
            agent_owner=self.agent_owner,
            job_type=job_type,
            run_id=f"{self.agent_name.lower().replace(' ', '_')}_{int(start_time)}",
            status=status,
            items_discovered=total_analyses,
            items_failed=0,
            items_succeeded=total_analyses,
            run_duration_ms=round(duration_ms, 2),
            token_usage=token_usage,
            api_calls_count=len(tools_used) + 1,
            item_name="excel_analysis",
        )

        self.learning.record_execution(
            request=user_request,
            tools_used=tools_used,
            success=(status == "success"),
            duration=duration_ms / 1000,
            error=error_msg,
        )

        return results