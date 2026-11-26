import aspose.cells as cells

from app.pipeline.execution_pipeline import ExecutionPipeline


def _build_numeric_workbook(tmp_path):
    wb = cells.Workbook()
    ws = wb.worksheets[0]
    ws.cells.get(0, 0).put_value("Amount")
    ws.cells.get(0, 1).put_value("Quantity")
    ws.cells.get(0, 2).put_value("Region")
    rows = [
        (10, 1, "north"),
        (20, 2, "south"),
        (30, 3, "north"),
        (40, 4, "west"),
    ]
    for row_index, row in enumerate(rows, start=1):
        for col_index, value in enumerate(row):
            ws.cells.get(row_index, col_index).put_value(value)

    path = str(tmp_path / "dataframe_tools.xlsx")
    wb.save(path)
    return path


def test_correlation_respects_column_selection(tmp_path):
    input_path = _build_numeric_workbook(tmp_path)

    result = ExecutionPipeline().execute(
        input_path,
        {
            "tools": ["correlation"],
            "columns": {"correlation": ["Amount"]},
        },
        output_path=str(tmp_path / "corr_out.xlsx"),
    )

    correlation = result["analysis_results"]["correlation"]

    assert set(correlation) == {"Amount"}


def test_pca_drops_rows_with_missing_values(tmp_path):
    wb = cells.Workbook()
    ws = wb.worksheets[0]
    ws.cells.get(0, 0).put_value("A")
    ws.cells.get(0, 1).put_value("B")
    rows = [(1, 2), (2, 4), (3, 6), (None, 8), (5, None)]
    for row_index, (a_value, b_value) in enumerate(rows, start=1):
        if a_value is not None:
            ws.cells.get(row_index, 0).put_value(a_value)
        if b_value is not None:
            ws.cells.get(row_index, 1).put_value(b_value)

    input_path = str(tmp_path / "pca_missing.xlsx")
    wb.save(input_path)

    result = ExecutionPipeline().execute(
        input_path,
        {"tools": ["pca"]},
        output_path=str(tmp_path / "pca_out.xlsx"),
    )

    pca = result["analysis_results"]["pca"]

    assert "error" not in pca
    assert pca["rows_used"] == 3
    assert pca["explained_variance"]
