from app.excel.reader import ExcelReader
from pathlib import Path

def test_read_excel():
    base_dir = Path(__file__).resolve().parents[1]
    file_path = base_dir / "samples" / "sales.xlsx"
    df = ExcelReader.load_sheet_as_dataframe(str(file_path))

    assert df.shape[0] > 0
    assert len(df.columns) > 0