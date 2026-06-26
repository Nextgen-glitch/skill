"""A demo check you can trigger on purpose, for verifying the heartbeat.

It surfaces a notice whenever a sentinel file exists, then consumes the file so it
surfaces exactly once. Create the file (e.g. `touch juno/state/TRIGGER`) to simulate a
condition the assistant notices while you're away. Real checks (watch for outreach
replies, follow-ups due, a morning brief) follow this same shape.
"""

from __future__ import annotations

from pathlib import Path

from juno.checks import Check, CheckResult, register_check


@register_check("trigger_watch")
def build(entry: dict) -> Check:
    trigger_file = Path(entry.get("trigger_file", "juno/state/TRIGGER"))
    level = entry.get("level", "interrupt")
    interval = int(entry.get("interval_seconds", 60))

    def run() -> CheckResult | None:
        if not trigger_file.exists():
            return None  # nothing noteworthy — quiet
        try:
            message = trigger_file.read_text(encoding="utf-8").strip()
        except OSError:
            message = ""
        trigger_file.unlink(missing_ok=True)  # consume so it surfaces once
        text = message or "The trigger condition fired."
        return CheckResult(text=text, level=level)

    return Check(name="trigger_watch", interval_seconds=interval, run=run)
