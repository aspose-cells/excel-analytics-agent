from app.excel.renderer import ChartRenderer
import aspose.cells as cells
from pathlib import Path

def test_chart_render_does_not_crash():
    base_dir = Path(__file__).resolve().parents[1]
    file_path = base_dir / "samples" / "sales.xlsx"

    wb = cells.Workbook(str(file_path))

    ws = wb.worksheets[0]
    ChartRenderer.add_line_chart(ws,ws.cells.min_data_row,ws.cells.max_data_column, 10)