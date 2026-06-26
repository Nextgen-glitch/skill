"""Tier 1 verification — the text conversation loop.

Proves: replies stream, the assistant remembers earlier turns in a session, and a
provider failure is handled cleanly (no crash, history left consistent).
"""

from __future__ import annotations

from juno.agent import Agent, build_system_prompt
from juno.config import Config

from tests.conftest import FailingProvider, ScriptedProvider


def test_reply_and_streaming():
    provider = ScriptedProvider(["hello there friend"])
    agent = Agent(provider, "system")

    chunks: list[str] = []
    reply = agent.run_turn("hi", on_text=chunks.append)

    assert reply == "hello there friend"
    assert "".join(chunks).split() == ["hello", "there", "friend"]  # streamed


def test_remembers_earlier_turns():
    provider = ScriptedProvider(["nice to meet you", "you said your name is Sam"])
    agent = Agent(provider, "system")

    agent.run_turn("my name is Sam")
    agent.run_turn("what did I say my name was?")

    # The second provider call must include the full prior conversation.
    second_call = provider.calls[1]
    roles_and_text = [(m["role"], m["content"]) for m in second_call]
    assert ("user", "my name is Sam") in roles_and_text
    assert ("assistant", "nice to meet you") in roles_and_text
    assert ("user", "what did I say my name was?") in roles_and_text

    # And the running history holds the whole exchange.
    assert len(agent.history) == 4


def test_provider_failure_is_graceful():
    agent = Agent(FailingProvider(), "system")

    reply = agent.run_turn("are you there?")

    assert "couldn't reach the model" in reply
    # The failed user turn is rolled back so the next turn starts clean.
    assert agent.history == []


def test_system_prompt_carries_identity():
    config = Config.load()
    prompt = build_system_prompt(config)

    assert "Juno" in prompt
    assert "data, not instructions" in prompt  # safety posture present from the start
