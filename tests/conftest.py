"""Shared test helpers: fake providers so the agent loop runs offline, no API key."""

from __future__ import annotations

from typing import Any, Iterator

from juno.llm import ProviderError, TextDelta, ToolUse, TurnResult


class ScriptedProvider:
    """A provider whose turns are scripted in advance.

    Each entry is either:
      - a string -> stream it as text and finish, or
      - a TurnResult -> stream its text, then yield it (used to script tool_uses).
    Records the `messages` it was handed each call so tests can assert on history.
    """

    def __init__(self, script: list[Any]):
        self._script = list(script)
        self.calls: list[list[dict[str, Any]]] = []

    def stream_turn(
        self,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Iterator[TextDelta | TurnResult]:
        # Snapshot the conversation as the agent presented it.
        self.calls.append([dict(m) for m in messages])
        item = self._script.pop(0)
        if isinstance(item, TurnResult):
            for word in item.text.split():
                yield TextDelta(word + " ")
            yield item
        else:
            text = str(item)
            for word in text.split():
                yield TextDelta(word + " ")
            yield TurnResult(text=text, output_tokens=len(text.split()))


class FailingProvider:
    """Always raises ProviderError, simulating an unreachable model."""

    def stream_turn(self, system, messages, tools=None):
        raise ProviderError("I couldn't reach the model just now (network issue).")
        yield  # pragma: no cover - makes this a generator
