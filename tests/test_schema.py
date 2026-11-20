import pandas as pd

from app.excel.schema import build_schema_summary


def test_schema_summary_contains_shape_and_columns():
    df = pd.DataFrame({"Year": [1, 2, 3], "Sales": [100, 110, 5000]})

    summary = build_schema_summary(df, file_name="sales.xlsx")

    assert "File: sales.xlsx" in summary
    assert "Rows: 3 | Columns: 2" in summary
    assert "Numeric columns: Year, Sales" in summary
    assert "Year | int64" in summary
    assert "min=1" in summary
    assert "max=5000" in summary
    assert "median=110" in summary


def test_schema_summary_detects_identifier_column():
    df = pd.DataFrame({
        "Customer": ["C0001", "C0002", "C0003"],
        "Amount": [10.0, 20.0, 30.0],
    })

    summary = build_schema_summary(df)

    assert "Other columns: Customer" in summary
    assert "sample=[C0001, C0002, C0003]" in summary
    assert "(likely identifier)" in summary


def test_schema_summary_flags_constant_column():
    df = pd.DataFrame({"Status": ["active", "active", "active"]})

    summary = build_schema_summary(df)

    assert "(constant)" in summary


def test_schema_summary_limits_sample_rows():
    df = pd.DataFrame({"A": list(range(10))})

    summary = build_schema_summary(df)

    assert "Sample rows (first 3):" in summary
    sample_lines = [
        line for line in summary.splitlines() if line.startswith("  ")
    ]
    assert len(sample_lines) == 3


def test_schema_summary_caps_columns():
    df = pd.DataFrame({f"c{i}": [i] for i in range(45)})

    summary = build_schema_summary(df, max_columns=40)

    assert "c39 | int64" in summary
    assert "c40 | int64" not in summary
    assert "... (5 more column(s) not shown)" in summary


def test_schema_summary_handles_empty_table():
    summary = build_schema_summary(pd.DataFrame())

    assert "Rows: 0 | Columns: 0" in summary
    assert "Sample rows" not in summary


def test_schema_summary_truncates_long_text():
    df = pd.DataFrame({"Note": ["x" * 100]})

    summary = build_schema_summary(df)

    assert "..." in summary
