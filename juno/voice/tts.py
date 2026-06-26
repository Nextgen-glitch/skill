"""Text-to-speech seam: give me text, play it aloud.

Two parts:
  - `Speaker`: the provider seam — synthesize a piece of text and play it (blocking),
    plus `stop()` to cut playback short. The reference build uses ElevenLabs.
  - `SentenceStreamer`: provider-agnostic glue that buffers streamed text and speaks it
    sentence by sentence, so the first sentence plays while the rest is still being
    written. This is what makes Juno feel responsive instead of laggy.
"""

from __future__ import annotations

import re
import threading
from typing import Protocol

# Speak a chunk once we have a sentence-ending punctuation mark (or on flush).
_SENTENCE_END = re.compile(r"(.+?[.!?])(\s|$)", re.DOTALL)


class Speaker(Protocol):
    """Synthesize and play a piece of text, blocking until done; stop() cuts it off."""

    def synth(self, text: str) -> None:
        ...

    def stop(self) -> None:
        ...


class SentenceStreamer:
    """Wraps a Speaker, accepting streamed text and speaking complete sentences early."""

    def __init__(self, speaker: Speaker):
        self._speaker = speaker
        self._buffer = ""
        self._interrupted = False

    def feed(self, chunk: str) -> None:
        """Accept a streamed text chunk; speak any complete sentences it completes."""
        if self._interrupted:
            return
        self._buffer += chunk
        while True:
            match = _SENTENCE_END.match(self._buffer)
            if not match:
                break
            sentence = match.group(1).strip()
            self._buffer = self._buffer[match.end():]
            if sentence:
                self._speaker.synth(sentence)
            if self._interrupted:
                self._buffer = ""
                return

    def flush(self) -> None:
        """Speak whatever text remains that didn't end in punctuation."""
        if self._interrupted:
            return
        remainder = self._buffer.strip()
        self._buffer = ""
        if remainder:
            self._speaker.synth(remainder)

    def interrupt(self) -> None:
        """Stop speaking now and drop any buffered text — the user is taking a turn."""
        self._interrupted = True
        self._buffer = ""
        self._speaker.stop()


class ElevenLabsSpeaker:
    """ElevenLabs implementation of the Speaker seam, streaming audio for low latency."""

    def __init__(self, api_key: str, voice_id: str, model: str = "eleven_turbo_v2_5"):
        from elevenlabs.client import ElevenLabs  # lazy import

        self._client = ElevenLabs(api_key=api_key)
        self._voice_id = voice_id
        self._model = model
        self._stop = threading.Event()

    def synth(self, text: str) -> None:
        from elevenlabs import stream as play_stream

        self._stop.clear()
        audio = self._client.text_to_speech.convert_as_stream(
            voice_id=self._voice_id,
            model_id=self._model,
            text=text,
        )
        # Stop early if interrupted: guard the byte stream with the stop flag.
        def guarded():
            for piece in audio:
                if self._stop.is_set():
                    return
                yield piece

        play_stream(guarded())

    def stop(self) -> None:
        self._stop.set()


def synthesize_bytes(text: str, api_key: str, voice_id: str, model: str = "eleven_turbo_v2_5") -> bytes:
    """Synthesize speech and return the full audio as MP3 bytes (for the web face).

    Unlike ElevenLabsSpeaker (which plays locally), this returns the bytes so a web
    endpoint can stream them to the browser. Lazy-imports the SDK so the text path and
    the demo brain don't need it installed.
    """
    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=api_key)
    audio = client.text_to_speech.convert(voice_id=voice_id, model_id=model, text=text)
    # The SDK yields byte chunks; join them into one MP3 payload.
    return b"".join(audio)


def build_speaker(config) -> Speaker:
    """Construct the speaker from config. The one place that knows the vendor + voice."""
    from juno.config import Config

    voice = config.section("voice")
    voice_id = voice.get("elevenlabs_voice_id", "")
    if not voice_id:
        raise RuntimeError(
            "No ElevenLabs voice selected. Set voice.elevenlabs_voice_id in config.toml."
        )
    api_key = Config.require_secret("ELEVENLABS_API_KEY")
    return ElevenLabsSpeaker(
        api_key=api_key,
        voice_id=voice_id,
        model=voice.get("elevenlabs_model", "eleven_turbo_v2_5"),
    )
