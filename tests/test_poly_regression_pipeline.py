import aspose.cells as cells
from app.pipeline.execution_pipeline import ExecutionPipeline


def test_poly_regression_pipeline_excel(tmp_path):
    # 1. Build an Excel file with rise-and-fall data
    values = [1, 3, 6, 9, 11, 12, 11, 9, 6, 3]
    wb = cells.Workbook()
    ws = wb.worksheets[0]
    ws.cells.get(0, 0).put_value("sales")
    for i, v in enumerate(values):
        ws.cells.get(i + 1, 0).put_value(float(v))
    input_path = str(tmp_path / "curve_input.xlsx")
    wb.save(input_path)

    # 2. Run poly_regression through the execution pipeline
    pipeline = ExecutionPipeline()
    output_path = tmp_path / "curve_output.xlsx"
    result = pipeline.execute(
        input_path,
        {"tools": ["poly_regression"]},
        output_path=str(output_path),
    )

    # 3. Assert analysis result structure
    poly = result["analysis_results"]["poly_regression"]
    assert "sales" in poly
    assert poly["sales"]["r_squared"] > 0.9
    assert poly["sales"]["is_better_than_linear"] is True
    assert poly["sales"]["degree"] == 2

    # 4. Assert output Excel saved with results
    assert output_path.exists()
    wb_out = cells.Workbook(str(output_path))
    sheet_names = [ws.name for ws in wb_out.worksheets]
    assert "Analysis Summary" in sheet_names

    # poly fit curve image embedded in the first worksheet
    assert len(list(wb_out.worksheets[0].pictures)) >= 1

    summary_sheet = wb_out.worksheets.get("Analysis Summary")
    summary_text = str(summary_sheet.cells.get(3, 1).value)
    assert "poly_regression" in summary_text
