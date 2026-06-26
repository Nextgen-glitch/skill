"""Tier 3 verification — voice wraps the same brain, without forking it.

No audio hardware or API keys are needed: capture, STT, and TTS each sit behind a seam,
so fakes stand in. We verify the orchestration — same run_turn, sentence-by-sentence
speaking, interruption, and the WAV envelope.
"""

from __future__ import annotations

import wave
import io

from juno.agent import Agent
from juno.llm import ToolUse, TurnResult
from juno.tools.registry import Param, ToolRegistry
from juno.voice.capture import pcm_to_wav
from juno.voice.session import VoiceSession
from juno.voice.tts import SentenceStreamer

from tests.conftest import ScriptedProvider


class FakeRecorder:
    def __init__(self, audio: bytes = b"RIFFfake"):
        self._audio = audio

    def record(self) -> bytes:
        return self._audio


class FakeTranscriber:
    def __init__(self, text: str):
        self._text = text

    def transcribe(self, audio: bytes) -> str:
        return self._text


class RecordingSpeaker:
    """Captures spoken sentences; can run a hook after each (to simulate interrupt)."""

    def __init__(self, on_synth=None):
        self.spoken: list[str] = []
        self.stopped = False
        self._on_synth = on_synth

    def synth(self, text: str) -> None:
        self.spoken.append(text)
        if self._on_synth:
            self._on_synth(text)

    def stop(self) -> None:
        self.stopped = True


def test_spoken_turn_uses_the_same_brain():
    agent = Agent(ScriptedProvider(["On it."]), "system")
    speaker = RecordingSpeaker()
    heard: list[str] = []
    session = VoiceSession(
        agent,
        transcriber=FakeTranscriber("add bike shops in Zurich to my list"),
        speaker=speaker,
        recorder=FakeRecorder(),
        on_transcript=heard.append,
    )

    reply = session.take_turn()

    # The transcript was shown and fed into the same run_turn a typed turn uses.
    assert heard == ["add bike shops in Zurich to my list"]
    assert agent.history[0] == {
        "role": "user",
        "content": "add bike shops in Zurich to my list",
    }
    assert reply == "On it."
    assert speaker.spoken == ["On it."]  # and it was spoken aloud


def test_sentences_are_spoken_as_they_stream():
    agent = Agent(ScriptedProvider(["First sentence. Second sentence."]), "system")
    speaker = RecordingSpeaker()
    session = VoiceSession(
        agent, FakeTranscriber("hi"), speaker, FakeRecorder()
    )

    session.take_turn()

    # Each complete sentence was handed to the speaker separately (early playback).
    assert speaker.spoken == ["First sentence.", "Second sentence."]


def test_interrupt_stops_further_speech():
    agent = Agent(ScriptedProvider(["One. Two. Three."]), "system")

    # Set up a speaker that interrupts the session right after the first sentence.
    holder = {}

    def after_first(_text):
        holder["session"].interrupt()

    speaker = RecordingSpeaker(on_synth=after_first)
    session = VoiceSession(agent, FakeTranscriber("go"), speaker, FakeRecorder())
    holder["session"] = session

    session.take_turn()

    assert speaker.spoken == ["One."]  # stopped before "Two." / "Three."
    assert speaker.stopped is True


def test_voice_turn_runs_tools_too():
    reg = ToolRegistry()
    ran: list = []

    @reg.tool(name="ping", description="ping", parameters={}, consequential=False)
    def ping() -> str:
        ran.append(True)
        return "pong"

    provider = ScriptedProvider(
        [TurnResult(text="", tool_uses=[ToolUse("t1", "ping", {})]), "Done."]
    )
    agent = Agent(provider, "system", registry=reg)
    speaker = RecordingSpeaker()
    session = VoiceSession(agent, FakeTranscriber("ping it"), speaker, FakeRecorder())

    reply = session.take_turn()

    assert ran == [True]  # the same tool loop runs on a spoken turn
    assert reply == "Done."


def test_sentence_streamer_flush_speaks_trailing_text():
    speaker = RecordingSpeaker()
    streamer = SentenceStreamer(speaker)
    streamer.feed("no terminal punctuation here")
    assert speaker.spoken == []  # nothing complete yet
    streamer.flush()
    assert speaker.spoken == ["no terminal punctuation here"]


def test_pcm_to_wav_is_readable():
    pcm = b"\x00\x01" * 1600  # 100 ms of 16-bit mono @ 16 kHz
    wav_bytes = pcm_to_wav(pcm)
    with wave.open(io.BytesIO(wav_bytes), "rb") as w:
        assert w.getnchannels() == 1
        assert w.getsampwidth() == 2
        assert w.getframerate() == 16_000
