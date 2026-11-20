import aspose.cells as cells

from app.pipeline.execution_pipeline import ExecutionPipeline


HEADERS = ["A", "B", "C", "Name"]
ROWS = [
    (10, 1, 100, "x"),
    (12, 2, 200, "y"),
    (11, 3, 300, "z"),
    (13, 4, 400, "w"),
    (1000, 5, 500, "v"),
]


def _build_workbook(tmp_path):
    wb = cells.Workbook()
    ws = wb.worksheets[0]
    for col, header in enumerate(HEADERS):
        ws.cells.get(0, col).put_value(header)
    for row, values in enumerate(ROWS, start=1):
        for col, value in enumerate(values):
            ws.cells.get(row, col).put_value(value)

    input_path = str(tmp_path / "selection_input.xlsx")
    wb.save(input_path)
    return input_path


def _run(tmp_path, plan):
    input_path = _build_workbook(tmp_path)
    output_path = tmp_path / "selection_output.xlsx"
    result = ExecutionPipeline().execute(
        input_path, plan, output_path=str(output_path)
    )
    return result["analysis_results"]


def test_plan_restricts_tool_to_one_column(tmp_path):
    analysis = _run(tmp_path, {
        "tools": ["outlier"],
        "columns": {"outlier": ["A"]},
    })

    assert set(analysis["outlier"]) == {"A"}
    assert analysis["outlier"]["A"]


def test_string_column_selection_is_accepted(tmp_path):
    analysis = _run(tmp_path, {
        "tools": ["outlier"],
        "columns": {"outlier": "A"},
    })

    assert set(analysis["outlier"]) == {"A"}


def test_partial_selection_skips_unknown_columns(tmp_path):
    analysis = _run(tmp_path, {
        "tools": ["statistics"],
        "columns": {"statistics": ["A", "DoesNotExist"]},
    })

    assert set(analysis["statistics"]) == {"A"}


def test_unknown_column_falls_back_to_all_numeric(tmp_path):
    analysis = _run(tmp_path, {
        "tools": ["statistics"],
        "columns": {"statistics": ["DoesNotExist"]},
    })

    assert set(analysis["statistics"]) == {"A", "B", "C"}


def test_text_column_selection_falls_back_to_numeric(tmp_path):
    analysis = _run(tmp_path, {
        "tools": ["statistics"],
        "columns": {"statistics": ["Name"]},
    })

    assert set(analysis["statistics"]) == {"A", "B", "C"}


def test_no_columns_key_keeps_existing_behaviour(tmp_path):
    analysis = _run(tmp_path, {"tools": ["statistics"]})

    assert set(analysis["statistics"]) == {"A", "B", "C"}


def test_hypothesis_respects_column_selection(tmp_path):
    analysis = _run(tmp_path, {
        "tools": ["hypothesis"],
        "columns": {"hypothesis": ["A", "B"]},
    })

    assert analysis["hypothesis"]["test_type"] == "t_test_ind"


def test_data_profile_ignores_column_selection(tmp_path):
    analysis = _run(tmp_path, {
        "tools": ["data_profile"],
        "columns": {"data_profile": ["A"]},
    })

    assert set(analysis["data_profile"]["columns"]) == set(HEADERS)
