import app.agents.excel_agent as agent_module
from app.agents.excel_agent import ExcelAgent, _summarize_analysis_items


class _StubRouter:
    def __init__(self, plan):
        self.plan = plan

    def route(self, file_path, request):
        return self.plan, 10


class _StubExecutor:
    def __init__(self, analysis_results):
        self.analysis_results = analysis_results

    def execute(self, file_path, plan, output_path=None):
        return {
            "row_count": 2,
            "column_count": 1,
            "numeric_columns": ["A"],
            "analysis_results": self.analysis_results,
            "summary": "",
        }


class _StubReporter:
    def generate(self, results, output_path):
        return None


class _StubLearning:
    def __init__(self):
        self.records = []

    def record_execution(self, **kwargs):
        self.records.append(kwargs)


def _build_agent(analysis_results):
    agent = ExcelAgent.__new__(ExcelAgent)
    agent.router = _StubRouter({"tools": ["pca"]})
    agent.executor = _StubExecutor(analysis_results)
    agent.reporter = _StubReporter()
    agent.learning = _StubLearning()
    agent.agent_name = "Test Agent"
    agent.agent_owner = "tester"
    return agent


def test_summary_counts_error_entries_as_failures():
    succeeded, failed = _summarize_analysis_items(
        {
            "statistics": {"A": {"mean": 1.0}},
            "pca": {"error": "boom"},
        }
    )

    assert succeeded == 1
    assert failed == 1


def test_agent_reports_failure_when_every_tool_fails(monkeypatch, tmp_path):
    captured = {}
    monkeypatch.setattr(
        agent_module,
        "send_agent_metrics",
        lambda **kwargs: captured.update(kwargs),
    )

    agent = _build_agent({"pca": {"error": "boom"}})
    agent.run(
        str(tmp_path / "in.xlsx"),
        str(tmp_path / "out.xlsx"),
        "analyze",
    )

    assert captured["status"] == "failure"
    assert captured["items_failed"] == 1
    assert captured["items_succeeded"] == 0


def test_agent_reports_partial_when_some_tools_fail(monkeypatch, tmp_path):
    captured = {}
    monkeypatch.setattr(
        agent_module,
        "send_agent_metrics",
        lambda **kwargs: captured.update(kwargs),
    )

    agent = _build_agent(
        {
            "statistics": {"A": {"mean": 1.0}},
            "pca": {"error": "boom"},
        }
    )
    agent.run(
        str(tmp_path / "in.xlsx"),
        str(tmp_path / "out.xlsx"),
        "analyze",
    )

    assert captured["status"] == "partial"
    assert captured["items_failed"] == 1
    assert captured["items_succeeded"] == 1
