"""Juno entrypoint — the text REPL (Tier 1).

Run with `juno` or `python -m juno.main`. The typed interface is the debug path and
the graceful fallback, and it stays alive forever — voice (Tier 3) is layered on top,
never a replacement.
"""

from __future__ import annotations

import sys

from typing import Any

from juno.agent import Agent, build_system_prompt
from juno.config import Config, MissingSecret
from juno.llm import build_provider
from juno.tools.registry import build_registry


def _stream_to_stdout(chunk: str) -> None:
    sys.stdout.write(chunk)
    sys.stdout.flush()


def _show_tool(name: str, tool_input: dict[str, Any], result: str) -> None:
    # Transparency: show every tool call and its result, dimmed, above the reply.
    args = ", ".join(f"{k}={v!r}" for k, v in tool_input.items())
    sys.stdout.write(f"\n  \033[2m· {name}({args})\033[0m\n")
    sys.stdout.flush()


def run_text_repl() -> int:
    config = Config.load()
    name = config.get("agent", "name", "Juno")

    try:
        provider = build_provider(config)
    except MissingSecret as err:
        print(f"{name} can't start: {err}")
        return 1

    agent = Agent(provider, build_system_prompt(config), registry=build_registry())

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
        agent.run_turn(user_text, on_text=_stream_to_stdout, on_tool=_show_tool)
        print("\n")


def main() -> None:
    sys.exit(run_text_repl())


if __name__ == "__main__":
    main()
