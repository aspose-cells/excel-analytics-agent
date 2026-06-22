import aspose.cells as cells
from aspose.pydrawing import Color
from aspose.cells import BackgroundType

from app.logger import logger


class Formatter:
    """Formatter for applying visual highlights to anomaly cells."""

    @staticmethod
    def apply_highlights(
        worksheet,
        results: dict,
        start_row: int = 0,
        start_col: int = 0,
    ) -> None:
        """Highlight anomaly cells with a red background and bold white text.

        Args:
            worksheet: The target worksheet.
            results: Dictionary containing anomaly data under the ``anomaly`` key.
            start_row: Row offset for the data region (default 0).
            start_col: Column offset for the data region (default 0).
        """
        try:
            anomaly_results = results.get("anomaly", {})

            cells_obj = worksheet.cells
            max_col = cells_obj.max_data_column

            for column_name, anomalies in anomaly_results.items():

                if not anomalies:
                    continue

                excel_col = -1

                for c in range(start_col, max_col + 1):
                    header_value = cells_obj.get(start_row, c).string_value
                    if header_value == column_name:
                        excel_col = c
                        break

                if excel_col == -1:
                    logger.warning(
                        f"Column '{column_name}' not found in worksheet"
                    )
                    continue

                for item in anomalies:
                    pandas_index = item["index"]
                    excel_row = start_row + 1 + pandas_index

                    cell = cells_obj.get(excel_row, excel_col)
                    style = cell.get_style()

                    style.foreground_color = Color.red
                    style.pattern = BackgroundType.SOLID

                    font = style.font
                    font.color = Color.white
                    font.is_bold = True

                    cell.set_style(style)

            logger.info("Highlights applied successfully")
        except Exception as e:
            logger.error(f"Failed to apply highlights: {e}")
            raise