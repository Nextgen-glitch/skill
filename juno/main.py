"""Juno entrypoint — the text REPL (Tier 1).

Run with `juno` or `python -m juno.main`. The typed interface is the debug path and
the graceful fallback, and it stays alive forever — voice (Tier 3) is layered on top,
never a replacement.
"""

from __future__ import annotations

import sys

from juno.agent import Agent, build_system_prompt
from juno.config import Config, MissingSecret
from juno.llm import build_provider


def _stream_to_stdout(chunk: str) -> None:
    sys.stdout.write(chunk)
    sys.stdout.flush()


def run_text_repl() -> int:
    config = Config.load()
    name = config.get("agent", "name", "Juno")

    try:
        provider = build_provider(config)
    except MissingSecret as err:
        print(f"{name} can't start: {err}")
        return 1

    agent = Agent(provider, build_system_prompt(config))

    print(f"{name} here — warm up, type a message. (exit / quit / Ctrl-D to leave)\n")
    while True:
        try:
            user_text = input("you ▸ ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{name}: talk soon.")
            return 0

        if not user_text:
            continue
        if user_text.lower() in {"exit", "quit"}:
            print(f"{name}: talk soon.")
            return 0

        print(f"{name} ▸ ", end="")
        agent.run_turn(user_text, on_text=_stream_to_stdout)
        print("\n")


def main() -> None:
    sys.exit(run_text_repl())


if __name__ == "__main__":
    main()
