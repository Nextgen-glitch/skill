"""The provider seam.

One small surface whose only job is: "send this conversation, get back a reply (or a
request to use a tool)." Everything else in the harness calls a Provider and never
touches a vendor SDK directly. This is what lets us swap models, add retries, and log
cost in exactly one place.

The seam streams text deltas as they arrive (so the UI feels alive and, in Tier 3,
voice can start speaking early) and returns a single TurnResult at the end carrying any
tool-use requests, the stop reason, and token usage.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Iterator, Protocol


# --- events the seam yields ------------------------------------------------------

@dataclass
class TextDelta:
    """A chunk of assistant text, streamed as it is generated."""

    text: str


@dataclass
class ToolUse:
    """A request from the model to run a tool. Acted on by the agent loop (Tier 2)."""

    id: str
    name: str
    input: dict[str, Any]


@dataclass
class TurnResult:
    """The end-of-turn summary. Yielded exactly once, last."""

    text: str
    tool_uses: list[ToolUse] = field(default_factory=list)
    stop_reason: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0


class ProviderError(RuntimeError):
    """A provider call failed in a way the agent should report cleanly, not crash on."""


# --- the interface ---------------------------------------------------------------

class Provider(Protocol):
    """Anything that can turn a conversation into a streamed reply."""

    def stream_turn(
        self,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Iterator[TextDelta | TurnResult]:
        ...


# --- the Anthropic implementation ------------------------------------------------

# Error types worth retrying. Imported lazily so the module imports without the SDK.
_RETRYABLE_NAMES = {
    "APIConnectionError",
    "APITimeoutError",
    "RateLimitError",
    "InternalServerError",
    "OverloadedError",
}


class AnthropicProvider:
    """Wraps the official Anthropic SDK with streaming + bounded retries."""

    def __init__(
        self,
        model: str,
        api_key: str,
        max_tokens: int = 2048,
        temperature: float = 1.0,
        max_retries: int = 4,
        request_timeout_seconds: float = 60.0,
    ):
        import anthropic  # imported here so the rest of the harness imports without it

        self._anthropic = anthropic
        self._client = anthropic.Anthropic(api_key=api_key, timeout=request_timeout_seconds)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_retries = max_retries

    def _is_retryable(self, err: Exception) -> bool:
        return type(err).__name__ in _RETRYABLE_NAMES

    def stream_turn(
        self,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Iterator[TextDelta | TurnResult]:
        kwargs: dict[str, Any] = dict(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system,
            messages=messages,
        )
        if tools:
            kwargs["tools"] = tools

        attempt = 0
        while True:
            started = False  # have we yielded any text yet this attempt?
            try:
                with self._client.messages.stream(**kwargs) as stream:
                    for text in stream.text_stream:
                        started = True
                        yield TextDelta(text)
                    final = stream.get_final_message()
                yield self._to_result(final)
                return
            except Exception as err:  # noqa: BLE001 - normalize everything to ProviderError
                # Once text has streamed out we cannot safely retry without duplicating
                # the reply, so surface it as a clean error instead.
                if started or not self._is_retryable(err) or attempt >= self.max_retries:
                    raise ProviderError(self._explain(err)) from err
                delay = 2 ** attempt  # 1, 2, 4, 8 ...
                time.sleep(delay)
                attempt += 1

    def _to_result(self, message: Any) -> TurnResult:
        text_parts: list[str] = []
        tool_uses: list[ToolUse] = []
        for block in message.content:
            btype = getattr(block, "type", None)
            if btype == "text":
                text_parts.append(block.text)
            elif btype == "tool_use":
                tool_uses.append(
                    ToolUse(id=block.id, name=block.name, input=dict(block.input or {}))
                )
        usage = getattr(message, "usage", None)
        return TurnResult(
            text="".join(text_parts),
            tool_uses=tool_uses,
            stop_reason=getattr(message, "stop_reason", None),
            input_tokens=getattr(usage, "input_tokens", 0) if usage else 0,
            output_tokens=getattr(usage, "output_tokens", 0) if usage else 0,
        )

    @staticmethod
    def _explain(err: Exception) -> str:
        name = type(err).__name__
        if name in {"APIConnectionError", "APITimeoutError"}:
            return "I couldn't reach the model just now (network issue). Try again in a moment."
        if name == "RateLimitError":
            return "We're being rate-limited. Give it a few seconds and try again."
        if name in {"InternalServerError", "OverloadedError"}:
            return "The model service is having a moment. Try again shortly."
        if name == "AuthenticationError":
            return "The API key was rejected. Check ANTHROPIC_API_KEY in your .env."
        return f"The model call failed: {err}"


def build_provider(config) -> Provider:
    """Construct the provider named in config.toml. The one place that knows the vendor."""
    from juno.config import Config

    model_cfg = config.section("model")
    provider_name = model_cfg.get("provider", "anthropic")
    if provider_name != "anthropic":
        raise ProviderError(f"Unknown model provider: {provider_name!r}")
    api_key = Config.require_secret("ANTHROPIC_API_KEY")
    return AnthropicProvider(
        model=model_cfg.get("name", "claude-opus-4-8"),
        api_key=api_key,
        max_tokens=model_cfg.get("max_tokens", 2048),
        temperature=model_cfg.get("temperature", 1.0),
        max_retries=model_cfg.get("max_retries", 4),
        request_timeout_seconds=model_cfg.get("request_timeout_seconds", 60),
    )
