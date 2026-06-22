from app.logger import logger
from app.exceptions import PipelineError
from app.excel.writer import ExcelWriter
from typing import Any, Dict


class ReportPipeline:
    """Pipeline that generates a report from analysis results."""

    def generate(self, results: Dict[str, Any], output_path: str) -> None:
        """Generate and write the report to the given path.

        Args:
            results: Dict of analysis results.
            output_path: Path where the report will be saved.
        """
        try:
            ExcelWriter.write_report(
                output_path=output_path,
                reports=results
            )
            logger.info("Report generated.")
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise PipelineError(f"Failed to generate report: {e}") from e