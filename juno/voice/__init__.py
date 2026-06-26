"""Voice adapters — the ears and mouth wrapped around the same brain.

Nothing here forks the agent logic: a spoken turn is transcribed to text and fed into
the very same `Agent.run_turn` a typed turn uses. STT and TTS each sit behind a thin
seam so the provider can change in one place.
"""
