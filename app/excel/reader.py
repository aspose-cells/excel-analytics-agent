import aspose.cells as cells
import pandas as pd

from app.logger import logger
from app.exceptions import ExcelReadError


class ExcelReader:
    """Reader for loading Excel worksheets into pandas DataFrames."""

    @staticmethod
    def load_sheet_as_dataframe(
        file_path: str, sheet_index: int = 0
    ) -> pd.DataFrame:
        """Load an Excel worksheet as a pandas DataFrame.

        Args:
            file_path: Path to the Excel file.
            sheet_index: Index of the worksheet to load (default 0).

        Returns:
            DataFrame with the first row used as column headers.

        Raises:
            ExcelReadError: If reading the Excel file fails.
        """
        try:
            workbook = cells.Workbook(file_path)
            worksheet = workbook.worksheets[sheet_index]

            cells_obj = worksheet.cells

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

            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        except Exception as e:
            logger.error(f"Failed to read Excel file '{file_path}': {e}")
            raise ExcelReadError(
                f"Failed to read Excel file '{file_path}'"
            ) from e