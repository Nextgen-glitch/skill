"""Speech-to-text seam: give me audio, get back text.

One small surface so the transcriber can be swapped without touching the rest. The
reference build uses Deepgram (fast, accurate, streaming). The key lives in the
environment, never in code.
"""

from __future__ import annotations

from typing import Protocol


class Transcriber(Protocol):
    """Anything that turns recorded audio (16-bit PCM WAV bytes) into text."""

    def transcribe(self, audio: bytes) -> str:
        ...


class DeepgramTranscriber:
    """Deepgram implementation of the STT seam."""

    def __init__(self, api_key: str, model: str = "nova-2"):
        from deepgram import DeepgramClient  # lazy: text path installs without it

        self._client = DeepgramClient(api_key)
        self._model = model

    def transcribe(self, audio: bytes) -> str:
        from deepgram import PrerecordedOptions

        options = PrerecordedOptions(model=self._model, smart_format=True, punctuate=True)
        source = {"buffer": audio, "mimetype": "audio/wav"}
        response = self._client.listen.prerecorded.v("1").transcribe_file(source, options)
        # Pull the top transcript out of Deepgram's response shape.
        return (
            response.results.channels[0].alternatives[0].transcript  # type: ignore[attr-defined]
        ).strip()


def build_transcriber(config) -> Transcriber:
    """Construct the transcriber named in config. The one place that knows the vendor."""
    from juno.config import Config

    voice = config.section("voice")
    api_key = Config.require_secret("DEEPGRAM_API_KEY")
    return DeepgramTranscriber(api_key=api_key, model=voice.get("deepgram_model", "nova-2"))
