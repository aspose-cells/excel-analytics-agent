import os
import aspose.cells as cells

from app.logger import logger
from app.exceptions import ExcelWriteError


class ExcelWriter:
    """Writer for saving report data to Excel files."""

    @staticmethod
    def write_report(output_path: str, reports: dict) -> None:
        """Write a dictionary of report data to an Excel file.

        If the file already exists (i.e. the executor already saved the
        workbook with source data, results and the Analysis Summary sheet)
        this method is a no-op to avoid duplicate watermark sheets.

        Args:
            output_path: Destination file path for the output Excel file.
            reports: Dictionary mapping report names to their values.

        Raises:
            ExcelWriteError: If writing the Excel file fails.
        """
        if os.path.isfile(output_path):
            logger.info(
                "Report workbook already exists at '%s' — skipping duplicate save",
                output_path,
            )
            return

        try:
            workbook = cells.Workbook()
            sheet = workbook.worksheets[0]

            row = 0

            for key, value in reports.items():
                sheet.cells.get(row, 0).put_value(str(key))
                sheet.cells.get(row, 1).put_value(str(value))
                row += 1

            workbook.save(output_path)
            logger.info(f"Report written to '{output_path}'")
        except Exception as e:
            logger.error(f"Failed to write Excel file '{output_path}': {e}")
            raise ExcelWriteError(
                f"Failed to write Excel file '{output_path}'"
            ) from e