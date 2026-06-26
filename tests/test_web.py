"""The browser face uses the same agent core; the demo brain drives the real loop."""

from __future__ import annotations

from juno.agent import Agent
from juno.tools.registry import build_registry
from juno.web import DemoProvider, handle_chat, synthesize, transcribe, _decode_audio


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


def test_handle_chat_collects_tools():
    result = handle_chat(_demo_agent(), "find bike shops in Zurich")
    assert "reply" in result
    assert [t["name"] for t in result["tools"]] == ["search_businesses"]


def test_synthesize_falls_back_without_key():
    # No key / no voice id -> None, which the page reads as "use browser speech".
    assert synthesize("hello", api_key=None, voice_id="", model="m") is None
    assert synthesize("hello", api_key="k", voice_id="", model="m") is None
    assert synthesize("", api_key="k", voice_id="v", model="m") is None


def test_transcribe_without_key_signals_fallback():
    # No Deepgram key -> None -> page falls back to browser speech recognition.
    assert transcribe(b"\x00\x01", api_key=None, model="nova-2", mimetype="audio/webm") is None


def test_transcribe_probe_with_key_returns_empty_not_none():
    # Empty audio + key present -> "" so the page detects Deepgram is available.
    assert transcribe(b"", api_key="k", model="nova-2", mimetype="audio/webm") == ""


def test_decode_audio_handles_empty_and_bad_input():
    assert _decode_audio("") == b""
    assert _decode_audio("not!!base64") == b""
    import base64
    assert _decode_audio(base64.b64encode(b"hi").decode()) == b"hi"
