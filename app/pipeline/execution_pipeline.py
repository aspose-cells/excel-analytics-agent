from app.logger import logger
from app.exceptions import PipelineError
from app.excel.reader import ExcelReader
from app.registry.tool_registry import TOOL_REGISTRY

from aspose.cells import Workbook
from aspose.cells import BackgroundType
from aspose.pydrawing import Color
from app.excel.formatter import Formatter
from app.excel.renderer import ChartRenderer
from app.excel.comment_writer import CommentWriter

from app.llm.explanation_generator import NarrativeGenerator
from typing import Any, Dict, List


class ExecutionPipeline:
    """Pipeline that executes analysis tools against an Excel file."""

    def execute(self, file_path: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the analysis plan against the given Excel file.

        Args:
            file_path: Path to the Excel file.
            plan: Dict containing 'tools' list and optional configuration.

        Returns:
            Dict with row_count, column_count, numeric_columns,
            analysis_results, and summary.
        """
        # =====================================
        # 1. Load dataframe
        # =====================================

        try:
            df = ExcelReader.load_sheet_as_dataframe(file_path)
        except Exception as e:
            logger.error(f"Failed to load Excel file: {e}")
            raise PipelineError(f"Failed to load Excel file: {e}") from e

        numeric_df = df.select_dtypes(include=['number'])

        numeric_columns: List[str] = numeric_df.columns.tolist()

        results: Dict[str, Any] = {}

        # =====================================
        # 2. Load workbook
        # =====================================

        try:
            wb = Workbook(file_path)
        except Exception as e:
            logger.error(f"Failed to load workbook: {e}")
            raise PipelineError(f"Failed to load workbook: {e}") from e

        ws = wb.worksheets[0]

        # =====================================
        # 3. Execute tools
        # =====================================

        tools = plan.get("tools", [])

        if not isinstance(tools, list):
            tools = [tools]

        for tool_name in tools:

            logger.info(f"Running tool: {tool_name}")

            tool_entry = TOOL_REGISTRY.get(tool_name)

            if not tool_entry:

                logger.error(f"Tool not found: {tool_name}")

                continue

            tool_func = tool_entry["func"]

            tool_input_type = tool_entry["input"]

            try:

                # =====================================
                # SERIES TOOLS
                # =====================================

                if tool_input_type == "series":

                    tool_results: Dict[str, Any] = {}

                    for col_idx, col in enumerate(numeric_columns):

                        values = (
                            numeric_df[col]
                            .dropna()
                            .astype(float)
                            .tolist()
                        )

                        if len(values) < 3:
                            continue

                        result = tool_func(values)

                        tool_results[col] = result

                        # =====================================
                        # CLUSTERING SPECIAL HANDLING
                        # =====================================

                        if tool_name == "clustering":

                            clusters = result["clusters"]

                            # header
                            ws.cells.get(
                                ws.cells.min_data_row,
                                ws.cells.max_data_column + 1
                            ).put_value(f"{col}_Cluster")

                            maxdataColumn = ws.cells.max_data_column
                            for idx, cluster_id in enumerate(clusters):

                                excel_row = ws.cells.min_data_row + idx + 1

                                cell = ws.cells.get(
                                    excel_row,
                                    maxdataColumn
                                )

                                cell.put_value(cluster_id)

                                style = wb.create_style()

                                if cluster_id == 0:

                                    style.foreground_color = Color.light_blue

                                elif cluster_id == 1:

                                    style.foreground_color = Color.light_green

                                else:

                                    style.foreground_color = Color.red

                                style.pattern = BackgroundType.SOLID

                                cell.set_style(style)

                    results[tool_name] = tool_results

                # =====================================
                # DATAFRAME TOOLS
                # =====================================

                elif tool_input_type == "dataframe":

                    results[tool_name] = tool_func(
                        numeric_df
                    )

                # =====================================
                # UNKNOWN
                # =====================================

                else:

                    logger.error(
                        f"Unsupported tool type: "
                        f"{tool_input_type}"
                    )

            except Exception as e:

                logger.error(f"Tool execution failed for {tool_name}: {e}")
                results[tool_name] = {
                    "error": str(e)
                }

        first_row = ws.cells.min_data_row
        first_col = ws.cells.min_data_column
        row_count = ws.cells.max_data_row - first_row + 1

        # =====================================
        # 4. Generate Summary
        # =====================================

        try:
            summary = NarrativeGenerator.generate(results)
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            summary = ""

        # =====================================
        # 5. Highlight anomalies
        # =====================================

        try:
            Formatter.apply_highlights(
                ws,
                results,
                first_row,
                first_col
            )
        except Exception as e:
            logger.error(f"Failed to apply highlights: {e}")

        # =====================================
        # 6. Generate charts
        # =====================================

        try:
            ChartRenderer.add_line_chart(
                ws, first_row, first_col, row_count
            )
        except Exception as e:
            logger.error(f"Failed to add charts: {e}")

        # =====================================
        # 7. Add comments
        # =====================================

        try:
            CommentWriter.add_comments(
                ws,
                results
            )
        except Exception as e:
            logger.error(f"Failed to add comments: {e}")

        # =====================================
        # 8. Save workbook
        # =====================================

        try:
            wb.save(file_path)
        except Exception as e:
            logger.error(f"Failed to save workbook: {e}")
            raise PipelineError(f"Failed to save workbook: {e}") from e

        # =====================================
        # 9. Final result
        # =====================================

        final_result: Dict[str, Any] = {

            "row_count": len(df),

            "column_count": len(df.columns),

            "numeric_columns": numeric_columns,

            "analysis_results": results,

            "summary": summary
        }

        return final_result
