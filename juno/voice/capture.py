"""Push-to-talk audio capture.

Record while a key is held, stop when it's released. Push-to-talk means we never have
to guess when the user started or finished — the single biggest simplification in a
first voice build, and it sidesteps the assistant hearing itself.
"""

from __future__ import annotations

import io
import wave
from typing import Protocol

SAMPLE_RATE = 16_000  # 16 kHz mono is plenty for speech and keeps STT fast.
CHANNELS = 1


class Recorder(Protocol):
    """Blocks until one push-to-talk utterance is captured; returns WAV bytes."""

    def record(self) -> bytes:
        ...


def pcm_to_wav(pcm: bytes, sample_rate: int = SAMPLE_RATE) -> bytes:
    """Wrap raw 16-bit mono PCM in a WAV container the transcriber can read."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(CHANNELS)
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        wav.writeframes(pcm)
    return buf.getvalue()


class PushToTalkRecorder:
    """Records from the default mic while a key is held (sounddevice + pynput)."""

    def __init__(self, key_name: str = "space", on_start=None, on_stop=None):
        self._key_name = key_name
        self._on_start = on_start  # e.g. a "listening…" cue
        self._on_stop = on_stop  # e.g. a "thinking…" cue shown the instant the key lifts

    def record(self) -> bytes:
        import numpy as np
        import sounddevice as sd
        from pynput import keyboard

        target = self._resolve_key(keyboard)
        frames: list = []
        held = {"down": False, "done": False}

        def on_press(key):
            if key == target and not held["down"]:
                held["down"] = True
                if self._on_start:
                    self._on_start()

        def on_release(key):
            if key == target and held["down"]:
                held["done"] = True
                if self._on_stop:
                    self._on_stop()
                return False  # stop the listener

        def callback(indata, frames_count, time_info, status):  # noqa: ARG001
            if held["down"]:
                frames.append(indata.copy())

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        with sd.InputStream(
            samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="int16", callback=callback
        ):
            listener.join()  # blocks until the key is released

        if not frames:
            return b""
        pcm = np.concatenate(frames, axis=0).tobytes()
        return pcm_to_wav(pcm)

    def _resolve_key(self, keyboard):
        name = self._key_name.lower()
        special = getattr(keyboard.Key, name, None)
        if special is not None:
            return special
        return keyboard.KeyCode.from_char(name)
