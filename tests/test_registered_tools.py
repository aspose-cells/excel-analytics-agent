import numpy as np
import aspose.cells as cells
import pytest

from app.registry.tool_registry import TOOL_REGISTRY
from app.pipeline.execution_pipeline import ExecutionPipeline


NEW_TOOLS = ["change_point", "distribution", "outlier", "seasonality", "smoothing"]


def test_new_tools_are_registered():
    for name in NEW_TOOLS:
        assert name in TOOL_REGISTRY, f"{name} is not registered"
        assert TOOL_REGISTRY[name]["input"] == "series"
        assert callable(TOOL_REGISTRY[name]["func"])


def test_change_point_detects_jump():
    values = [1.0, 1.0, 1.0, 1.0, 10.0, 10.0, 10.0, 10.0]

    result = TOOL_REGISTRY["change_point"]["func"](values)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["position"] == 3
    assert result[0]["change"] == pytest.approx(9.0)


def test_change_point_returns_empty_for_smooth_data():
    result = TOOL_REGISTRY["change_point"]["func"]([1.0, 2.0, 3.0, 4.0, 5.0])

    assert result == []


def test_distribution_accepts_normal_data():
    np.random.seed(0)
    values = np.random.normal(0, 1, 300).tolist()

    result = TOOL_REGISTRY["distribution"]["func"](values)

    assert set(result) == {"statistic", "pvalue", "is_normal"}
    assert result["is_normal"] is True
    assert result["pvalue"] > 0.05


def test_distribution_rejects_skewed_data():
    np.random.seed(0)
    values = np.random.exponential(1.0, 300).tolist()

    result = TOOL_REGISTRY["distribution"]["func"](values)

    assert result["is_normal"] is False
    assert result["pvalue"] <= 0.05


def test_outlier_finds_extreme_value():
    np.random.seed(0)
    values = np.random.normal(10, 1, 100).tolist()
    values.append(1000.0)

    result = TOOL_REGISTRY["outlier"]["func"](values)

    assert len(result) >= 1
    assert any(item["value"] == 1000.0 for item in result)


def test_outlier_returns_empty_for_clean_data():
    np.random.seed(0)
    values = np.random.normal(0, 1, 100).tolist()

    result = TOOL_REGISTRY["outlier"]["func"](values)

    assert result == []


def test_seasonality_returns_three_components():
    values = [1.0, 2.0, 3.0, 4.0] * 3

    result = TOOL_REGISTRY["seasonality"]["func"](values)

    assert set(result) == {"trend", "seasonal", "residual"}
    for component in result.values():
        assert len(component) == len(values)


def test_smoothing_returns_moving_average():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]

    result = TOOL_REGISTRY["smoothing"]["func"](values)

    assert len(result) == len(values)
    assert np.isnan(result[0])
    assert result[-1] == pytest.approx(4.0)


def test_all_new_tools_run_through_pipeline(tmp_path):
    values = ([10.0, 12.0, 11.0] * 5
              + [30.0, 32.0, 31.0] * 4
              + [500.0])

    wb = cells.Workbook()
    ws = wb.worksheets[0]
    ws.cells.get(0, 0).put_value("Value")
    for i, value in enumerate(values, start=1):
        ws.cells.get(i, 0).put_value(float(value))

    input_path = str(tmp_path / "tools_input.xlsx")
    wb.save(input_path)

    output_path = tmp_path / "tools_output.xlsx"
    result = ExecutionPipeline().execute(
        input_path,
        {"tools": NEW_TOOLS},
        output_path=str(output_path),
    )

    analysis = result["analysis_results"]
    for name in NEW_TOOLS:
        assert name in analysis
        assert "error" not in analysis[name]

    assert analysis["change_point"]["Value"]
    assert analysis["distribution"]["Value"]["is_normal"] is False
    assert analysis["outlier"]["Value"]
    assert len(analysis["seasonality"]["Value"]["trend"]) == len(values)
    assert len(analysis["smoothing"]["Value"]) == len(values)

    assert output_path.exists()

    wb_out = cells.Workbook(str(output_path))
    summary_sheet = wb_out.worksheets.get("Analysis Summary")
    summary_text = str(summary_sheet.cells.get(3, 1).value)
    for name in NEW_TOOLS:
        assert name in summary_text

    narrative = str(summary_sheet.cells.get(4, 1).value)
    assert "change point" in narrative
    assert "normal distribution" in narrative
    assert "IQR outlier" in narrative
    assert "seasonal decomposition completed" in narrative
    assert "moving average smoothing completed" in narrative
