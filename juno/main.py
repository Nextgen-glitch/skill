"""Juno entrypoint — text REPL (Tier 1) and push-to-talk voice (Tier 3).

Run with `juno` (text) or `juno --voice` (push-to-talk). The typed interface is the
debug path and the graceful fallback, and it stays alive forever — voice is layered on
top of the same brain, never a replacement.
"""

from __future__ import annotations

import argparse
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


def _console_confirmer(name: str, tool_input: dict) -> bool:
    """Interactive confirmation prompt — states plainly what's about to happen."""
    from juno.safety import describe_action

    try:
        answer = input(
            f"\n  \033[33m⚠ allow: {describe_action(name, tool_input)} ? [y/N]\033[0m "
        ).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return answer in {"y", "yes"}


def _build_agent(config, confirmer=_console_confirmer) -> tuple[Agent, "object"]:
    """Construct the agent: provider, durable memory, tools, gate, and audit.

    Shared by the text and voice front-ends so both flow through the same brain — and
    the same confirmation gate. Returns (agent, audit).
    """
    from juno.audit import build_audit
    from juno.memory import MemoryStore
    from juno.safety import ConfirmationGate
    from juno.tools.memory_tools import bind_memory

    provider = build_provider(config)

    mem_cfg = config.section("memory")
    store = MemoryStore(mem_cfg.get("store_path", "juno/state/memory.json"))
    bind_memory(store)  # so the remember/update/forget tools act on this store
    memory_block = store.prompt_block(mem_cfg.get("max_facts_in_prompt", 100))
    system_prompt = build_system_prompt(config, memory_block)

    audit = build_audit(config)
    gate = ConfirmationGate(
        confirm_required=set(config.get("safety", "confirm_required_tools", [])),
        confirmer=confirmer,
        audit=audit,
    )
    agent = Agent(
        provider,
        system_prompt,
        registry=build_registry(),
        gate=gate,
        audit=audit,
        model_name=config.get("model", "name", ""),
    )
    return agent, audit


def _build_heartbeat(config, announcer):
    """Construct the inbox + heartbeat from config. Returns (heartbeat, inbox)."""
    from juno.checks import build_checks
    from juno.heartbeat import Heartbeat
    from juno.inbox import Inbox
    from juno.safety import is_paused

    hb = config.section("heartbeat")
    inbox = Inbox(hb.get("inbox_path", "juno/state/inbox.json"))
    heartbeat = Heartbeat(
        checks=build_checks(config),
        inbox=inbox,
        schedule_path=hb.get("schedule_path", "juno/state/schedule.json"),
        quiet_hours=(hb.get("quiet_hours_start", 22), hb.get("quiet_hours_end", 8)),
        announcer=announcer,
        is_paused=lambda: is_paused(config),  # the kill switch, checked every tick
    )
    return heartbeat, inbox


def _print_notice(name: str, notice) -> None:
    print(f"\n  \033[36m🔔 {name} (from {notice.source}): {notice.text}\033[0m")


def run_text_repl() -> int:
    config = Config.load()
    name = config.get("agent", "name", "Juno")

    try:
        agent, audit = _build_agent(config)
    except MissingSecret as err:
        print(f"{name} can't start: {err}")
        return 1

    heartbeat, inbox = _build_heartbeat(
        config, announcer=lambda n: _print_notice(name, n)
    )

    print(f"{name} here — warm up, type a message. (exit / quit / Ctrl-D to leave)")
    print(
        "  commands: 'inbox', 'dismiss <id>', 'pause'/'resume' (kill switch), 'cost'.\n"
    )

    # Catch up on anything that happened while I was away — held, not lost.
    held = heartbeat.catch_up()
    if held:
        print(f"  while you were gone ({len(held)}):")
        for n in held:
            print(f"    #{n.id} [{n.level}] {n.text}")
        print()

    if config.section("heartbeat").get("enabled", False):
        heartbeat.start(config.get("heartbeat", "tick_seconds", 60))

    try:
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
            if _handle_inbox_command(user_text, inbox):
                continue
            if _handle_control_command(user_text, config, audit):
                continue

            print(f"{name} ▸ ", end="")
            agent.run_turn(user_text, on_text=_stream_to_stdout, on_tool=_show_tool)
            print("\n")
    finally:
        heartbeat.stop()


def _handle_control_command(text: str, config, audit) -> bool:
    """Handle 'pause' / 'resume' (kill switch) and 'cost'. Returns True if handled."""
    from juno.safety import is_paused, set_paused

    lowered = text.lower()
    if lowered == "pause":
        set_paused(config, True)
        print("  ⏸ proactive behavior paused. You can still talk to me.\n")
        return True
    if lowered == "resume":
        set_paused(config, False)
        print("  ▶ proactive behavior resumed.\n")
        return True
    if lowered == "status":
        print(f"  proactive: {'paused' if is_paused(config) else 'running'}\n")
        return True
    if lowered == "cost":
        print(f"  model usage so far: {audit.tally.summary()}\n")
        return True
    return False


def _handle_inbox_command(text: str, inbox) -> bool:
    """Handle 'inbox' / 'dismiss <id>'. Returns True if the input was a command."""
    lowered = text.lower()
    if lowered == "inbox":
        pending = inbox.pending()
        if not pending:
            print("  inbox is empty.\n")
        else:
            for n in pending:
                print(f"  #{n.id} [{n.level}] {n.text}")
            print()
        return True
    if lowered.startswith("dismiss "):
        try:
            notice_id = int(text.split(None, 1)[1])
        except (ValueError, IndexError):
            print("  usage: dismiss <id>\n")
            return True
        print(("  dismissed.\n" if inbox.dismiss(notice_id) else "  no such notice.\n"))
        return True
    return False


def run_voice_repl() -> int:
    """Push-to-talk loop. Wraps the same agent; the text path is unaffected."""
    config = Config.load()
    name = config.get("agent", "name", "Juno")

    try:
        agent, _audit = _build_agent(config)
        from juno.voice.capture import PushToTalkRecorder
        from juno.voice.session import VoiceSession
        from juno.voice.stt import build_transcriber
        from juno.voice.tts import build_speaker
    except MissingSecret as err:
        print(f"{name} can't start in voice mode: {err}")
        return 1
    except ModuleNotFoundError as err:
        print(f"Voice extras not installed ({err.name}). Run: pip install -e \".[voice]\"")
        return 1
    except RuntimeError as err:  # e.g. no ElevenLabs voice chosen yet
        print(f"{name} can't start in voice mode: {err}")
        return 1

    key = config.get("voice", "push_to_talk_key", "space")
    recorder = PushToTalkRecorder(
        key_name=key,
        on_start=lambda: print("\n  ● listening…", end="", flush=True),
        on_stop=lambda: print("  ◐ thinking…", flush=True),
    )
    session = VoiceSession(
        agent,
        transcriber=build_transcriber(config),
        speaker=build_speaker(config),
        recorder=recorder,
        on_transcript=lambda t: print(f"  you (heard) ▸ {t}"),
        on_tool=_show_tool,
    )

    # A new push of the talk key while Juno is speaking interrupts the reply.
    _wire_interrupt(session, key)

    print(f"{name} voice — hold [{key}] to talk, release to send. Ctrl-C to leave.")
    try:
        while True:
            reply = session.take_turn()
            if reply:
                print(f"  {name} ▸ {reply}\n")
    except KeyboardInterrupt:
        print(f"\n{name}: talk soon.")
        return 0


def _wire_interrupt(session, key_name: str) -> None:
    """Start a background listener so pressing the talk key cuts off playback."""
    try:
        from pynput import keyboard
    except ModuleNotFoundError:
        return

    name = key_name.lower()
    target = getattr(keyboard.Key, name, None) or keyboard.KeyCode.from_char(name)

    def on_press(k):
        if k == target:
            session.interrupt()

    keyboard.Listener(on_press=on_press).start()


def main() -> None:
    parser = argparse.ArgumentParser(prog="juno", description="Juno assistant")
    parser.add_argument(
        "--voice", action="store_true", help="push-to-talk voice mode (Tier 3)"
    )
    args = parser.parse_args()
    sys.exit(run_voice_repl() if args.voice else run_text_repl())


if __name__ == "__main__":
    main()
