import json

import pytest

try:
    import app.llm.planner as planner_module
    from app.llm.planner import Planner
    from app.llm.prompts.tool_selection_prompt import TOOL_SELECTION_PROMPT
    _IMPORT_ERROR = None
except Exception as e:  # pragma: no cover - only when no API key is set
    _IMPORT_ERROR = e

pytestmark = pytest.mark.skipif(
    _IMPORT_ERROR is not None,
    reason=f"planner unavailable: {_IMPORT_ERROR}",
)


class _Usage:
    total_tokens = 42


class _Message:
    content = json.dumps({
        "tools": ["kde"],
        "columns": {"kde": ["Amount"]},
        "reason": "Amount is bimodal",
        "confidence": 0.9,
    })


class _Choice:
    def __init__(self):
        self.message = _Message()


class _FakeResponse:
    def __init__(self):
        self.usage = _Usage()
        self.choices = [_Choice()]


def _patch_client(monkeypatch, captured):
    def fake_create(**kwargs):
        captured.update(kwargs)
        return _FakeResponse()

    monkeypatch.setattr(
        planner_module.client.chat.completions, "create", fake_create
    )


def test_plan_includes_schema_in_user_message(monkeypatch):
    captured = {}
    _patch_client(monkeypatch, captured)

    plan, tokens = Planner().create_plan(
        "analyze customer spending",
        schema="Rows: 500 | Columns: 2",
    )

    user_message = captured["messages"][1]["content"]
    assert "analyze customer spending" in user_message
    assert "Rows: 500 | Columns: 2" in user_message
    assert "untrusted" in user_message.lower()
    assert plan["tools"] == ["kde"]
    assert plan["columns"] == {"kde": ["Amount"]}
    assert tokens == 42


def test_plan_without_schema_sends_request_only(monkeypatch):
    captured = {}
    _patch_client(monkeypatch, captured)

    Planner().create_plan("analyze sales")

    assert captured["messages"][1]["content"] == "analyze sales"


def test_prompt_requests_column_selection():
    assert '"columns"' in TOOL_SELECTION_PROMPT
    assert "untrusted" in TOOL_SELECTION_PROMPT.lower()
