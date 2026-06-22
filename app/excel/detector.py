from app.logger import logger


class ColumnDetector:
    """Detector for identifying numeric columns in an Excel worksheet."""

    def detect_numeric_columns(self, sheet) -> list[int]:
        """Detect columns that contain numeric values.

        Args:
            sheet: The target worksheet.

        Returns:
            List of column indices (0-based) that contain at least one numeric value.
        """
        try:
            numeric_columns = []

            max_col = sheet.cells.max_data_column
            max_row = sheet.cells.max_data_row

            for col in range(max_col + 1):
                numeric_count = 0

                for row in range(1, max_row + 1):
                    value = sheet.cells.get(row, col).value
                    if isinstance(value, (int, float)):
                        numeric_count += 1

                if numeric_count > 0:
                    numeric_columns.append(col)

            return numeric_columns
        except Exception as e:
            logger.error(f"Failed to detect numeric columns: {e}")
            raise