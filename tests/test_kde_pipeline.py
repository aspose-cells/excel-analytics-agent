import numpy as np
import aspose.cells as cells

from app.pipeline.execution_pipeline import ExecutionPipeline


def test_kde_pipeline_excel(tmp_path):
    np.random.seed(0)
    values = np.concatenate([
        np.random.normal(100, 15, 200),
        np.random.normal(800, 20, 200),
    ])

    # 1. Build Excel with a single bimodal numeric column
    wb = cells.Workbook()
    ws = wb.worksheets[0]
    ws.cells.get(0, 0).put_value("Amount")
    for i, v in enumerate(values, start=1):
        ws.cells.get(i, 0).put_value(float(v))
    input_path = str(tmp_path / "kde_input.xlsx")
    wb.save(input_path)

    # 2. Run the kde tool through the pipeline
    pipeline = ExecutionPipeline()
    output_path = tmp_path / "kde_output.xlsx"
    result = pipeline.execute(
        input_path,
        {"tools": ["kde"]},
        output_path=str(output_path),
    )

    # 3. Bimodal detection
    kde = result["analysis_results"]["kde"]["Amount"]
    assert kde["n_modes"] == 2
    assert kde["is_multimodal"] is True

    locations = sorted(kde["mode_locations"])
    assert 60 < locations[0] < 140
    assert 740 < locations[1] < 860

    # 4. Output Excel saved with an embedded KDE chart
    assert output_path.exists()
    wb_out = cells.Workbook(str(output_path))
    assert len(list(wb_out.worksheets[0].pictures)) >= 1

    summary_sheet = wb_out.worksheets.get("Analysis Summary")
    summary_text = str(summary_sheet.cells.get(3, 1).value)
    assert "kde" in summary_text
