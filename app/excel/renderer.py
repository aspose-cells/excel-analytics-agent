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
        """Add or update a line chart on the worksheet.

        If a chart already exists, its data series are updated in-place
        (avoids Aspose.Cells save persistence bug with chart removal).

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

            existing = list(ws.charts)
            if existing:
                chart = existing[0]
                chart.n_series.clear()
                chart.n_series.add(value_range, True)
                chart.n_series.category_data = category_range
                chart.title.text = "Analysis Result"
                if chart.n_series.length > 0:
                    chart.n_series[0].data_labels.show_value = True
            else:
                chart_index = ws.charts.add(ChartType.LINE, 5, 5, 25, 15)
                chart = ws.charts[chart_index]
                chart.n_series.add(value_range, True)
                chart.n_series.category_data = category_range
                chart.title.text = "Analysis Result"
                if chart.n_series.length > 0:
                    chart.n_series[0].data_labels.show_value = True

            logger.info("Line chart added/updated successfully")
        except Exception as e:
            logger.error(f"Failed to add line chart: {e}")
            raise