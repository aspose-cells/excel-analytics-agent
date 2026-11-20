import pytest

try:
    from app.pipeline.routing_pipeline import RoutingPipeline
    _IMPORT_ERROR = None
except Exception as e:  # pragma: no cover - only when no API key is set
    _IMPORT_ERROR = e

pytestmark = pytest.mark.skipif(
    _IMPORT_ERROR is not None,
    reason=f"routing pipeline unavailable: {_IMPORT_ERROR}",
)

import aspose.cells as cells


class _FakePlanner:
    def __init__(self):
        self.request = None
        self.schema = None

    def create_plan(self, request, schema=None):
        self.request = request
        self.schema = schema
        return {"tools": ["trend"]}, 0


def _build_workbook(tmp_path):
    wb = cells.Workbook()
    ws = wb.worksheets[0]
    ws.cells.get(0, 0).put_value("Amount")
    ws.cells.get(0, 1).put_value("Customer")
    for row in range(1, 6):
        ws.cells.get(row, 0).put_value(float(row * 10))
        ws.cells.get(row, 1).put_value(f"C{row:03d}")

    path = str(tmp_path / "routing.xlsx")
    wb.save(path)
    return path


def test_route_passes_schema_to_planner(tmp_path):
    router = RoutingPipeline.__new__(RoutingPipeline)
    router.planner = _FakePlanner()

    path = _build_workbook(tmp_path)
    plan, tokens = router.route(path, "analyze amounts")

    assert plan == {"tools": ["trend"]}
    assert tokens == 0
    assert router.planner.request == "analyze amounts"
    assert "Amount" in router.planner.schema
    assert "Customer" in router.planner.schema
    assert "Rows: 5" in router.planner.schema


def test_route_continues_without_schema_on_read_error(tmp_path):
    router = RoutingPipeline.__new__(RoutingPipeline)
    router.planner = _FakePlanner()

    plan, _ = router.route(str(tmp_path / "missing.xlsx"), "analyze")

    assert plan == {"tools": ["trend"]}
    assert router.planner.schema is None
