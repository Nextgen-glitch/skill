"""The browser face uses the same agent core; the demo brain drives the real loop."""

from __future__ import annotations

from juno.agent import Agent
from juno.tools.registry import build_registry
from juno.web import DemoProvider


def _demo_agent() -> Agent:
    return Agent(DemoProvider(), "system", registry=build_registry())


def test_demo_brain_runs_calendar_tool():
    seen = []
    reply = _demo_agent().run_turn(
        "what's on my calendar today?", on_tool=lambda n, i, r: seen.append(n)
    )
    assert seen == ["list_calendar_events"]
    assert "Events for today" in reply


def test_demo_brain_runs_search_tool():
    seen = []
    _demo_agent().run_turn("find bike shops in Zurich", on_tool=lambda n, i, r: seen.append(n))
    assert seen == ["search_businesses"]


def test_demo_brain_plain_reply_without_tool():
    seen = []
    reply = _demo_agent().run_turn("hello there", on_tool=lambda n, i, r: seen.append(n))
    assert seen == []
    assert "demo mode" in reply
