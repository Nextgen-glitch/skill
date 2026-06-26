"""Tier 6 verification — the rails.

Proves: consequential tools are stopped until an explicit per-action yes; read-only
tools run freely; approval doesn't generalize; an unattended consequential action falls
to the safe default (deny); the gate is config-driven; the audit log records what
happened with a cost tally; and the kill switch pauses proactivity without code edits.
"""

from __future__ import annotations

import json

from juno.agent import Agent
from juno.audit import AuditLog, CostTally
from juno.config import Config
from juno.llm import ToolUse, TurnResult
from juno.safety import ConfirmationGate, is_paused, set_paused
from juno.tools.registry import Param, ToolRegistry

from tests.conftest import ScriptedProvider


def _send_registry(sent: list) -> ToolRegistry:
    reg = ToolRegistry()

    @reg.tool(
        name="send_email",
        description="Send an email.",
        parameters={"to": Param("string", "recipient")},
        consequential=True,  # declares itself gated
    )
    def send_email(to: str) -> str:
        sent.append(to)
        return f"sent to {to}"

    @reg.tool(
        name="search_businesses",
        description="Read-only search.",
        parameters={"niche": Param("string", "niche")},
        consequential=False,
    )
    def search_businesses(niche: str) -> str:
        return f"results for {niche}"

    return reg


def test_consequential_tool_blocked_until_yes():
    sent: list = []
    reg = _send_registry(sent)
    asked: list = []

    def confirmer(name, tool_input):
        asked.append((name, tool_input))
        return False  # the user says no

    gate = ConfirmationGate({"send_email"}, confirmer=confirmer)
    provider = ScriptedProvider(
        [
            TurnResult(text="", tool_uses=[ToolUse("t1", "send_email", {"to": "a@b.com"})]),
            "Okay, I didn't send it.",
        ]
    )
    agent = Agent(provider, "system", registry=reg, gate=gate)

    reply = agent.run_turn("email a@b.com")

    assert asked == [("send_email", {"to": "a@b.com"})]  # it stopped and asked
    assert sent == []  # and did NOT send when refused
    assert reply == "Okay, I didn't send it."


def test_yes_lets_it_run():
    sent: list = []
    reg = _send_registry(sent)
    gate = ConfirmationGate({"send_email"}, confirmer=lambda n, i: True)
    provider = ScriptedProvider(
        [
            TurnResult(text="", tool_uses=[ToolUse("t1", "send_email", {"to": "x@y.com"})]),
            "Sent.",
        ]
    )
    agent = Agent(provider, "system", registry=reg, gate=gate)

    agent.run_turn("email x@y.com")
    assert sent == ["x@y.com"]


def test_read_only_tool_runs_without_asking():
    sent: list = []
    reg = _send_registry(sent)
    asked: list = []
    gate = ConfirmationGate({"send_email"}, confirmer=lambda n, i: asked.append(n) or True)
    provider = ScriptedProvider(
        [
            TurnResult(text="", tool_uses=[ToolUse("t1", "search_businesses", {"niche": "cafes"})]),
            "Here you go.",
        ]
    )
    agent = Agent(provider, "system", registry=reg, gate=gate)

    agent.run_turn("find cafes")
    assert asked == []  # read-only never prompted


def test_confirmation_is_per_action():
    sent: list = []
    reg = _send_registry(sent)
    answers = iter([True, False])  # yes the first time, no the second
    gate = ConfirmationGate({"send_email"}, confirmer=lambda n, i: next(answers))
    provider = ScriptedProvider(
        [
            TurnResult(text="", tool_uses=[ToolUse("a", "send_email", {"to": "1@x.com"})]),
            TurnResult(text="", tool_uses=[ToolUse("b", "send_email", {"to": "2@x.com"})]),
            "Done.",
        ]
    )
    agent = Agent(provider, "system", registry=reg, gate=gate)

    agent.run_turn("send two emails")
    assert sent == ["1@x.com"]  # the second send was asked again and refused


def test_unattended_consequential_action_is_denied():
    sent: list = []
    reg = _send_registry(sent)
    # confirmer=None models a heartbeat-initiated action with no human to ask.
    gate = ConfirmationGate({"send_email"}, confirmer=None)
    provider = ScriptedProvider(
        [
            TurnResult(text="", tool_uses=[ToolUse("t1", "send_email", {"to": "a@b.com"})]),
            "Held it for you.",
        ]
    )
    agent = Agent(provider, "system", registry=reg, gate=gate)

    agent.run_turn("send it")
    assert sent == []  # safe default: do nothing


def test_gate_is_config_driven():
    # A tool not self-declared consequential is still gated if config names it.
    reg = ToolRegistry()

    @reg.tool(name="change_setting", description="change a setting", parameters={}, consequential=False)
    def change_setting() -> str:
        return "changed"

    gate = ConfirmationGate({"change_setting"}, confirmer=lambda n, i: False)
    assert gate.is_consequential(name="change_setting", declared=False) is True


def test_audit_log_and_cost_tally(tmp_path):
    log = AuditLog(tmp_path / "audit.jsonl", tally=CostTally(input_per_mtok=1.0, output_per_mtok=2.0))
    log.model("claude", input_tokens=1_000_000, output_tokens=500_000)
    log.tool("send_email", {"to": "a@b"}, status="ran", result="sent")

    lines = (tmp_path / "audit.jsonl").read_text().strip().splitlines()
    kinds = [json.loads(l)["kind"] for l in lines]
    assert kinds == ["model", "tool"]
    # 1M in @ $1 + 0.5M out @ $2 = $2.00
    assert abs(log.tally.dollars - 2.0) < 1e-9


def test_kill_switch_toggles_via_flag_file(tmp_path, monkeypatch):
    config = Config.load()
    flag = tmp_path / "PAUSED"
    # Point the kill switch at a temp flag file without editing config.toml.
    monkeypatch.setitem(config._data, "killswitch", {"paused": False, "flag_file": str(flag)})

    assert is_paused(config) is False
    set_paused(config, True)
    assert flag.exists() and is_paused(config) is True
    set_paused(config, False)
    assert not flag.exists() and is_paused(config) is False
