import pandas as pd
import aspose.cells as cells

from app.analysis.data_profile import DataQualityAnalysis
from app.registry.tool_registry import TOOL_REGISTRY
from app.pipeline.execution_pipeline import ExecutionPipeline


def _messages(profile):
    return [issue["message"] for issue in profile["issues"]]


def test_data_profile_is_registered():
    assert "data_profile" in TOOL_REGISTRY
    assert TOOL_REGISTRY["data_profile"]["input"] == "dataframe"


def test_clean_table_has_no_issues():
    df = pd.DataFrame({
        "A": [1, 2, 3, 4, 5],
        "B": ["x", "y", "z", "w", "v"],
    })

    profile = DataQualityAnalysis.profile(df)

    assert profile["issues"] == []
    assert profile["quality_score"] == 100
    assert profile["table"]["rows"] == 5
    assert profile["table"]["columns"] == 2
    assert profile["table"]["duplicate_rows"] == 0


def test_missing_values_are_detected():
    df = pd.DataFrame({"A": [1.0, None, None, None, 5.0]})

    profile = DataQualityAnalysis.profile(df)

    column = profile["columns"]["A"]
    assert column["missing"] == 3
    assert column["missing_pct"] == 60.0
    assert any(
        issue["level"] == "ERROR" and issue["column"] == "A"
        for issue in profile["issues"]
    )


def test_duplicate_rows_are_detected():
    df = pd.DataFrame({"A": [1, 1, 1, 1], "B": ["x", "x", "x", "x"]})

    profile = DataQualityAnalysis.profile(df)

    assert profile["table"]["duplicate_rows"] == 3
    assert any("duplicate row" in message for message in _messages(profile))


def test_constant_column_is_flagged():
    df = pd.DataFrame({"A": [7, 7, 7], "B": [1, 2, 3]})

    profile = DataQualityAnalysis.profile(df)

    assert profile["columns"]["A"]["constant"] is True
    assert profile["columns"]["B"]["constant"] is False
    assert any("constant column" in message for message in _messages(profile))


def test_mixed_types_are_detected():
    df = pd.DataFrame({"A": [1, "two", 3, "four"]})

    profile = DataQualityAnalysis.profile(df)

    assert profile["columns"]["A"]["mixed_types"] is True
    assert any("mixed types" in message for message in _messages(profile))


def test_implausible_range_is_an_error():
    df = pd.DataFrame({"Sales": [100, 110, 120, 130, 343535130]})

    profile = DataQualityAnalysis.profile(df)

    errors = [i for i in profile["issues"] if i["level"] == "ERROR"]
    assert errors
    assert errors[0]["column"] == "Sales"
    assert "median" in errors[0]["message"]
    assert profile["quality_score"] < 100


def test_text_column_reports_whitespace():
    df = pd.DataFrame({"Name": [" alice", "bob ", "carol", "dave", "eve"]})

    profile = DataQualityAnalysis.profile(df)

    assert profile["columns"]["Name"]["whitespace"] == 2
    assert any("whitespace" in message for message in _messages(profile))


def test_numeric_text_is_flagged_but_still_profiled():
    df = pd.DataFrame({"Amount": ["100", "200", "300", "400", "500"]})

    profile = DataQualityAnalysis.profile(df)

    column = profile["columns"]["Amount"]
    assert column["min"] == 100.0
    assert column["max"] == 500.0
    assert any("stored as text" in message for message in _messages(profile))


def test_outliers_counted():
    df = pd.DataFrame({"A": [10, 11, 12, 13, 14, 15, 500]})

    profile = DataQualityAnalysis.profile(df)

    assert profile["columns"]["A"]["outliers"] == 1


def test_data_profile_pipeline_writes_sheet(tmp_path):
    wb = cells.Workbook()
    ws = wb.worksheets[0]
    headers = ["Name", "Sales", "Status"]
    for col, header in enumerate(headers):
        ws.cells.get(0, col).put_value(header)

    rows = [
        (" alice", 100, "active"),
        ("bob", 110, "active"),
        ("carol", 120, "active"),
        ("carol", 120, "active"),
        ("dave", 343535130, "active"),
        ("eve", None, "active"),
    ]
    for row, values in enumerate(rows, start=1):
        for col, value in enumerate(values):
            if value is not None:
                ws.cells.get(row, col).put_value(value)

    input_path = str(tmp_path / "profile_input.xlsx")
    wb.save(input_path)

    output_path = tmp_path / "profile_output.xlsx"
    result = ExecutionPipeline().execute(
        input_path,
        {"tools": ["data_profile"]},
        output_path=str(output_path),
    )

    profile = result["analysis_results"]["data_profile"]
    assert set(profile["columns"]) == set(headers)
    assert profile["table"]["duplicate_rows"] == 1
    assert profile["columns"]["Sales"]["missing"] == 1
    assert profile["columns"]["Status"]["constant"] is True
    assert profile["quality_score"] < 100

    assert "Data quality score" in result["summary"]
    assert "duplicate row" in result["summary"]

    assert output_path.exists()
    wb_out = cells.Workbook(str(output_path))
    quality = wb_out.worksheets.get("Data Quality")
    assert quality is not None

    written = []
    for row in range(0, 40):
        for col in range(0, 4):
            value = quality.cells.get(row, col).value
            if value is not None:
                written.append(str(value))
    text = " | ".join(written)

    assert "Data Quality Report" in text
    assert "quality_score" in text
    assert "Sales" in text
    assert "duplicate row" in text
