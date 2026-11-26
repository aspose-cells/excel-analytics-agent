import aspose.cells as cells
import pytest

from app.exceptions import PipelineError
from app.pipeline.execution_pipeline import ExecutionPipeline


def _build_workbook(tmp_path):
    wb = cells.Workbook()
    ws = wb.worksheets[0]
    ws.cells.get(0, 0).put_value("Value")
    for index in range(5):
        ws.cells.get(index + 1, 0).put_value(float(index))

    path = tmp_path / "input.xlsx"
    wb.save(str(path))
    return path


def test_missing_output_path_does_not_overwrite_input(tmp_path):
    input_path = _build_workbook(tmp_path)
    before = input_path.read_bytes()

    result = ExecutionPipeline().execute(
        str(input_path), {"tools": ["statistics"]}
    )

    assert input_path.read_bytes() == before
    assert (tmp_path / "input_analyzed.xlsx").exists()
    assert result["row_count"] == 5


def test_explicit_output_equal_to_input_is_rejected(tmp_path):
    input_path = _build_workbook(tmp_path)

    with pytest.raises(PipelineError):
        ExecutionPipeline().execute(
            str(input_path),
            {"tools": ["statistics"]},
            output_path=str(input_path),
        )

    assert input_path.exists()
