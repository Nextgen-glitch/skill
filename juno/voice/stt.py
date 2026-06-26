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
        self._api_key = api_key
        self._model = model

    def transcribe(self, audio: bytes) -> str:
        return transcribe_bytes(audio, self._api_key, self._model, mimetype="audio/wav")


def transcribe_bytes(
    audio: bytes, api_key: str, model: str = "nova-2", mimetype: str = "audio/webm"
) -> str:
    """Transcribe audio bytes with Deepgram. Used by the terminal and the web face.

    `mimetype` lets the browser send its native recording format (e.g. audio/webm;
    codecs=opus) without re-encoding. Lazy-imports the SDK so the text path installs light.
    """
    from deepgram import DeepgramClient, PrerecordedOptions

    client = DeepgramClient(api_key)
    options = PrerecordedOptions(model=model, smart_format=True, punctuate=True)
    source = {"buffer": audio, "mimetype": mimetype}
    response = client.listen.prerecorded.v("1").transcribe_file(source, options)
    return (
        response.results.channels[0].alternatives[0].transcript  # type: ignore[attr-defined]
    ).strip()


def build_transcriber(config) -> Transcriber:
    """Construct the transcriber named in config. The one place that knows the vendor."""
    from juno.config import Config

    voice = config.section("voice")
    api_key = Config.require_secret("DEEPGRAM_API_KEY")
    return DeepgramTranscriber(api_key=api_key, model=voice.get("deepgram_model", "nova-2"))
