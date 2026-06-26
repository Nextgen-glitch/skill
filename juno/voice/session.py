"""The voice turn — capture, transcribe, run the SAME brain, speak.

This orchestration is deliberately thin. The only difference from a typed turn is at the
two ends: input arrives by transcribing recorded speech, and output is spoken as well as
shown. The middle — `agent.run_turn` — is untouched and shared.
"""

from __future__ import annotations

from typing import Any, Callable

from juno.agent import Agent
from juno.voice.capture import Recorder
from juno.voice.stt import Transcriber
from juno.voice.tts import SentenceStreamer, Speaker

OnTranscript = Callable[[str], None]
OnStatus = Callable[[str], None]
OnTool = Callable[[str, dict[str, Any], str], None]


class VoiceSession:
    """Runs spoken turns through the shared agent core."""

    def __init__(
        self,
        agent: Agent,
        transcriber: Transcriber,
        speaker: Speaker,
        recorder: Recorder,
        on_transcript: OnTranscript | None = None,
        on_status: OnStatus | None = None,
        on_tool: OnTool | None = None,
    ):
        self.agent = agent
        self.transcriber = transcriber
        self.speaker = speaker
        self.recorder = recorder
        self.on_transcript = on_transcript
        self.on_status = on_status
        self.on_tool = on_tool
        self._streamer: SentenceStreamer | None = None

    def take_turn(self) -> str | None:
        """Capture one utterance and respond aloud. Returns the reply text, or None."""
        audio = self.recorder.record()  # blocks while the key is held
        if not audio:
            return None

        # Give an immediate sign the moment the key is released — silence reads as broken.
        if self.on_status:
            self.on_status("transcribing…")
        heard = self.transcriber.transcribe(audio)
        if not heard.strip():
            return None

        # Always show what we *thought* we heard, so a wrong answer is easy to diagnose.
        if self.on_transcript:
            self.on_transcript(heard)
        if self.on_status:
            self.on_status("thinking…")

        # Speak sentences as the reply streams; feed the SAME run_turn a typed turn uses.
        self._streamer = SentenceStreamer(self.speaker)
        reply = self.agent.run_turn(
            heard, on_text=self._streamer.feed, on_tool=self.on_tool
        )
        self._streamer.flush()
        self._streamer = None
        return reply

    def interrupt(self) -> None:
        """Stop speaking and drop buffered audio — the user is starting a new turn."""
        if self._streamer is not None:
            self._streamer.interrupt()
