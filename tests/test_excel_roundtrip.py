import aspose.cells as cells
from app.analysis.regression import RegressionAnalysis


def test_excel_roundtrip(tmp_path):
    # read -> analyze -> write -> reopen

    # 1. CREATE — build Excel with parabolic data y = x²
    wb = cells.Workbook()
    ws = wb.worksheets[0]
    ws.cells.get(0, 0).put_value("value")
    values = [float(i * i) for i in range(10)]
    for i, v in enumerate(values):
        ws.cells.get(i + 1, 0).put_value(v)
    input_path = str(tmp_path / "poly_input.xlsx")
    wb.save(input_path)

    # 2. READ — reopen and read values back
    wb2 = cells.Workbook(input_path)
    ws2 = wb2.worksheets[0]
    read_values = [ws2.cells.get(r, 0).value for r in range(1, 11)]
    assert read_values == values

    # 3. ANALYZE — run polynomial regression on the read values
    result = RegressionAnalysis.polynomial_regression(read_values, degree=2)
    assert result["r_squared"] > 0.99
    assert result["is_better_than_linear"] is True
    assert result["degree"] == 2

    # 4. WRITE — write results into a new "PolyRegression" sheet
    out_ws = wb2.worksheets.add("PolyRegression")
    out_ws.cells.get(0, 0).put_value("metric")
    out_ws.cells.get(0, 1).put_value("value")
    out_ws.cells.get(1, 0).put_value("r_squared")
    out_ws.cells.get(1, 1).put_value(result["r_squared"])
    out_ws.cells.get(2, 0).put_value("degree")
    out_ws.cells.get(2, 1).put_value(result["degree"])
    out_ws.cells.get(3, 0).put_value("is_better_than_linear")
    out_ws.cells.get(3, 1).put_value(str(result["is_better_than_linear"]))
    for j, c in enumerate(result["coefficients"]):
        out_ws.cells.get(4, j).put_value(float(c))
    output_path = str(tmp_path / "poly_output.xlsx")
    wb2.save(output_path)

    # 5. REOPEN — verify persisted results
    wb3 = cells.Workbook(output_path)
    sheet_names = [ws.name for ws in wb3.worksheets]
    assert "PolyRegression" in sheet_names

    saved = wb3.worksheets.get("PolyRegression")
    assert abs(saved.cells.get(1, 1).value - result["r_squared"]) < 1e-9
    assert saved.cells.get(2, 1).value == result["degree"]
    assert saved.cells.get(4, 0).value is not None
