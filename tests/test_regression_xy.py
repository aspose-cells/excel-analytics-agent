import aspose.cells as cells
import pytest

from app.analysis.regression import RegressionAnalysis
from app.exceptions import AnalysisError
from app.pipeline.execution_pipeline import ExecutionPipeline


def test_linear_regression_uses_supplied_x():
    x = [2000.0, 2001.0, 2002.0, 2003.0]
    y = [2 * value - 4000 for value in x]

    result = RegressionAnalysis.linear_regression(y, x_values=x)

    assert result["slope"] == pytest.approx(2.0)
    assert result["intercept"] == pytest.approx(-4000.0)
    assert result["rvalue"] == pytest.approx(1.0)
    assert result["x_source"] == "column"
    assert result["n"] == 4


def test_linear_regression_defaults_to_index_x():
    result = RegressionAnalysis.linear_regression([10.0, 20.0, 30.0])

    assert result["x_source"] == "index"
    assert result["slope"] == pytest.approx(10.0)


def test_linear_regression_rejects_length_mismatch():
    with pytest.raises(AnalysisError):
        RegressionAnalysis.linear_regression([1.0, 2.0], x_values=[1.0])


def test_linear_regression_rejects_constant_x():
    with pytest.raises(AnalysisError):
        RegressionAnalysis.linear_regression(
            [1.0, 2.0], x_values=[5.0, 5.0]
        )


def test_polynomial_regression_uses_supplied_x():
    x = [1000.0 + index for index in range(10)]
    y = [float((value - 1000) ** 2) for value in x]

    result = RegressionAnalysis.polynomial_regression(y, x_values=x)

    assert result["r_squared"] > 0.99
    assert result["x_source"] == "column"


def _build_workbook(tmp_path):
    wb = cells.Workbook()
    ws = wb.worksheets[0]
    ws.cells.get(0, 0).put_value("Year")
    ws.cells.get(0, 1).put_value("Sales")
    for index in range(8):
        year = 2000 + index
        ws.cells.get(index + 1, 0).put_value(year)
        ws.cells.get(index + 1, 1).put_value(3 * year - 5000)

    path = str(tmp_path / "xy_input.xlsx")
    wb.save(path)
    return path


def test_pipeline_fits_y_against_named_x(tmp_path):
    input_path = _build_workbook(tmp_path)
    output_path = tmp_path / "xy_output.xlsx"

    result = ExecutionPipeline().execute(
        input_path,
        {
            "tools": ["regression"],
            "xy": {"regression": {"x": "Year", "y": "Sales"}},
        },
        output_path=str(output_path),
    )

    regression = result["analysis_results"]["regression"]

    assert set(regression) == {"Sales"}
    assert regression["Sales"]["x_column"] == "Year"
    assert regression["Sales"]["x_source"] == "column"
    assert regression["Sales"]["slope"] == pytest.approx(3.0)


def test_pipeline_falls_back_when_xy_is_invalid(tmp_path):
    input_path = _build_workbook(tmp_path)
    output_path = tmp_path / "xy_fallback.xlsx"

    result = ExecutionPipeline().execute(
        input_path,
        {
            "tools": ["regression"],
            "xy": {"regression": {"x": "DoesNotExist", "y": "Sales"}},
        },
        output_path=str(output_path),
    )

    regression = result["analysis_results"]["regression"]

    assert "Year" in regression
    assert "Sales" in regression
    assert "x_column" not in regression["Sales"]


def test_poly_regression_stores_x_column_for_charts(tmp_path):
    input_path = _build_workbook(tmp_path)
    output_path = tmp_path / "xy_poly_output.xlsx"

    result = ExecutionPipeline().execute(
        input_path,
        {
            "tools": ["poly_regression"],
            "xy": {"poly_regression": {"x": "Year", "y": "Sales"}},
        },
        output_path=str(output_path),
    )

    poly = result["analysis_results"]["poly_regression"]

    assert set(poly) == {"Sales"}
    assert poly["Sales"]["x_column"] == "Year"
