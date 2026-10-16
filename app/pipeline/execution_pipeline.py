from app.logger import logger
from app.exceptions import PipelineError
from app.registry.tool_registry import TOOL_REGISTRY

from aspose.cells import Workbook
from aspose.cells import BackgroundType
from aspose.pydrawing import Color
from app.excel.formatter import Formatter
from app.excel.renderer import ChartRenderer
from app.excel.comment_writer import CommentWriter

from app.llm.explanation_generator import NarrativeGenerator
from typing import Any, Dict, List

import pandas as pd


def _worksheet_to_dataframe(ws) -> pd.DataFrame:
    """Convert an Aspose worksheet to a pandas DataFrame.

    Args:
        ws: An aspose.cells Worksheet object.

    Returns:
        DataFrame with the first row used as column headers.
    """
    cells_obj = ws.cells
    first_row = cells_obj.min_data_row
    first_col = cells_obj.min_data_column
    last_row = cells_obj.max_data_row
    last_col = cells_obj.max_data_column

    data = []
    for r in range(first_row, last_row + 1):
        row = []
        for c in range(first_col, last_col + 1):
            row.append(cells_obj.get(r, c).value)
        data.append(row)

    return pd.DataFrame(data[1:], columns=data[0])


class ExecutionPipeline:
    """Pipeline that executes analysis tools against an Excel file."""

    def execute(self, file_path: str, plan: Dict[str, Any],
                output_path: str | None = None) -> Dict[str, Any]:
        """Execute the analysis plan against the given Excel file.

        Args:
            file_path: Path to the input Excel file (read-only).
            plan: Dict containing 'tools' list and optional configuration.
            output_path: Path for the output Excel file. Source data is
                copied here with all results. If None, defaults to
                ``file_path`` (overwrites input).

        Returns:
            Dict with row_count, column_count, numeric_columns,
            analysis_results, and summary.
        """
        # =====================================
        # 1. Load workbook & dataframe
        # =====================================

        try:
            wb = Workbook(file_path)
        except Exception as e:
            logger.error(f"Failed to load workbook: {e}")
            raise PipelineError(f"Failed to load workbook: {e}") from e

        ws = wb.worksheets[0]
        df = _worksheet_to_dataframe(ws)

        numeric_df = df.select_dtypes(include=['number'])

        exclude_patterns = ("_Cluster", "_cluster", "_Label", "_label")
        numeric_df = numeric_df.loc[
            :, ~numeric_df.columns.str.endswith(exclude_patterns)
        ]

        numeric_columns: List[str] = numeric_df.columns.tolist()

        results: Dict[str, Any] = {}

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

                    # =====================================
                    # CLUSTERING: build existing column map
                    # =====================================

                    cluster_col_map: Dict[str, int] = {}
                    if tool_name == "clustering":
                        header_row = ws.cells.min_data_row
                        for c in range(ws.cells.min_data_column, ws.cells.max_data_column + 1):
                            cell_val = ws.cells.get(header_row, c).value
                            if cell_val and str(cell_val).lower().endswith(("_cluster", "_label")):
                                cluster_col_map[str(cell_val)] = c

                    # =====================================
                    # HYPOTHESIS: collect all columns for cross-column comparison
                    # =====================================

                    if tool_name == "hypothesis":
                        all_groups: List[List[float]] = []
                        for col in numeric_columns:
                            values = (
                                numeric_df[col]
                                .dropna()
                                .astype(float)
                                .tolist()
                            )
                            if len(values) >= 3:
                                all_groups.append(values)
                        if len(all_groups) >= 2:
                            results[tool_name] = tool_func(all_groups)
                        continue

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
                            header_row = ws.cells.min_data_row
                            col_name = f"{col}_Cluster"

                            if col_name in cluster_col_map:
                                target_col = cluster_col_map[col_name]
                            else:
                                target_col = ws.cells.max_data_column + 1
                                ws.cells.get(header_row, target_col).put_value(col_name)

                            for idx, cluster_id in enumerate(clusters):

                                excel_row = header_row + idx + 1

                                cell = ws.cells.get(
                                    excel_row,
                                    target_col
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
        # 6b. Render polynomial fit curves (matplotlib)
        # =====================================

        poly_results = results.get("poly_regression")
        if isinstance(poly_results, dict) and poly_results:
            try:
                ChartRenderer.add_poly_fit_chart(
                    ws, poly_results, numeric_df
                )
            except Exception as e:
                logger.error(f"Failed to add poly fit chart: {e}")

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
        # 8. Write meta-data to a separate sheet
        # =====================================

        try:
            existing = wb.worksheets.get("Analysis Summary")
            if existing:
                wb.worksheets.remove(existing)
            meta_sheet = wb.worksheets.add("Analysis Summary")
            meta = [
                ("row_count", str(len(df))),
                ("column_count", str(len(df.columns))),
                ("numeric_columns", str(numeric_columns)),
                ("analysis_results", str(results)),
                ("summary", str(summary)),
            ]
            for i, (k, v) in enumerate(meta):
                meta_sheet.cells.get(i, 0).put_value(k)
                meta_sheet.cells.get(i, 1).put_value(v)
        except Exception as e:
            logger.error(f"Failed to write meta-data sheet: {e}")

        # =====================================
        # 9. Save workbook to output path
        # =====================================

        try:
            save_path = output_path or file_path
            wb.save(save_path)
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
