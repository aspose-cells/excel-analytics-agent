from aspose.cells.charts import ChartType
from aspose.pydrawing import Color
from aspose.cells import BackgroundType
from aspose.cells import CellsHelper

from app.logger import logger


class ChartRenderer:
    """Renderer for adding charts to Excel worksheets."""

    @staticmethod
    def add_line_chart(
        ws, first_row: int, first_col: int, row_count: int
    ) -> None:
        """Add a line chart to the worksheet.

        The chart uses the column at ``first_col`` as the X-axis (categories)
        and the column at ``first_col + 1`` as the Y-axis (values).

        Args:
            ws: The target worksheet.
            first_row: Row index of the header row.
            first_col: Column index for categories (X axis).
            row_count: Number of data rows (excluding header).
        """
        try:
            data_start_row = first_row + 1
            data_end_row = first_row + row_count - 1

            category_col = first_col
            value_col = first_col + 1

            category_start = CellsHelper.cell_index_to_name(
                data_start_row, category_col
            )
            category_end = CellsHelper.cell_index_to_name(
                data_end_row, category_col
            )

            value_start = CellsHelper.cell_index_to_name(
                data_start_row, value_col
            )
            value_end = CellsHelper.cell_index_to_name(
                data_end_row, value_col
            )

            category_range = f"{category_start}:{category_end}"
            value_range = f"{value_start}:{value_end}"

            chart_index = ws.charts.add(ChartType.LINE, 5, 5, 25, 15)
            chart = ws.charts[chart_index]

            series_index = chart.n_series.add(value_range, True)
            chart.n_series.category_data = category_range

            series = chart.n_series[series_index]
            chart.title.text = "Analysis Result"
            series.data_labels.show_value = True

            logger.info("Line chart added successfully")
        except Exception as e:
            logger.error(f"Failed to add line chart: {e}")
            raise