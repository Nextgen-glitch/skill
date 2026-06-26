"""Tier 2 verification — the tool registry and the agent tool loop.

Proves: the model can call a tool, the harness runs it and feeds the result back, the
model weaves it into a reply; several tool calls can happen before the final answer;
and a failing tool comes back as a plain message instead of crashing.
"""

from __future__ import annotations

from juno.agent import Agent
from juno.llm import ToolUse, TurnResult
from juno.tools.registry import Param, ToolRegistry

from tests.conftest import ScriptedProvider


def _registry_with(calls: list, fail: bool = False) -> ToolRegistry:
    reg = ToolRegistry()

    @reg.tool(
        name="get_list",
        description="Return the user's list for today.",
        parameters={"day": Param("string", "Which day.", required=False, default="today")},
        consequential=False,
    )
    def get_list(day: str = "today") -> str:
        calls.append(day)
        if fail:
            raise RuntimeError("the list service is down")
        return f"List for {day}: milk, stamps, call the bank"

    return reg


def test_tool_result_is_woven_into_reply():
    calls: list = []
    reg = _registry_with(calls)
    provider = ScriptedProvider(
        [
            # First the model asks to use the tool...
            TurnResult(text="", tool_uses=[ToolUse(id="t1", name="get_list", input={})]),
            # ...then it answers using the result.
            "Here's your list: milk, stamps, call the bank.",
        ]
    )
    agent = Agent(provider, "system", registry=reg)

    reply = agent.run_turn("what's on my list today?")

    assert calls == ["today"]  # the tool actually ran
    assert "milk" in reply

    # The tool exchange is recorded in history in the API's expected shape.
    assistant_turn = agent.history[1]
    assert assistant_turn["role"] == "assistant"
    assert any(b["type"] == "tool_use" for b in assistant_turn["content"])
    tool_result_turn = agent.history[2]
    assert tool_result_turn["content"][0]["type"] == "tool_result"


def test_multiple_tool_calls_in_one_turn():
    calls: list = []
    reg = _registry_with(calls)
    provider = ScriptedProvider(
        [
            TurnResult(text="", tool_uses=[ToolUse("a", "get_list", {"day": "today"})]),
            TurnResult(text="", tool_uses=[ToolUse("b", "get_list", {"day": "tomorrow"})]),
            "Both days covered.",
        ]
    )
    agent = Agent(provider, "system", registry=reg)

    reply = agent.run_turn("compare today and tomorrow")

    assert calls == ["today", "tomorrow"]  # two sequential tool calls, one user turn
    assert reply == "Both days covered."


def test_tool_failure_is_explained_not_crashed():
    calls: list = []
    reg = _registry_with(calls, fail=True)
    seen: list = []
    provider = ScriptedProvider(
        [
            TurnResult(text="", tool_uses=[ToolUse("t1", "get_list", {})]),
            "Sorry — I couldn't pull your list; the service is down.",
        ]
    )
    agent = Agent(provider, "system", registry=reg)

    reply = agent.run_turn("my list?", on_tool=lambda n, i, r: seen.append(r))

    # The failure reached the model as a plain string, and nothing crashed.
    assert "failed" in seen[0]
    assert "down" in seen[0]
    assert reply.startswith("Sorry")


def test_bundled_stub_tools_register():
    from juno.tools.registry import build_registry

    reg = build_registry()
    assert "list_calendar_events" in reg.names()
    assert "search_businesses" in reg.names()
    # Read-only tools are not flagged consequential.
    assert reg.get("list_calendar_events").consequential is False
    # And they run, returning plain text.
    assert "Events for today" in reg.run("list_calendar_events", {"day": "today"})
