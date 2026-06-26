"""The heartbeat — a background loop that lets Juno act without being spoken to.

Separate from the conversation loop. On each tick it runs whichever checks are due,
routes anything noteworthy into the inbox, and decides whether it's worth actively
surfacing right now. Quiet by default: most checks report nothing, calm items just
accumulate, and only interrupt/critical items reach out — interrupt items wait for
waking hours.

The core is `tick(now)`, driven by an injectable clock, so behavior is deterministic and
testable without real sleeping. A thin threaded runner calls it on an interval. The loop
doesn't care which machine it's on — moving it to an always-on host is a relocation, not
a rewrite.
"""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

from juno.checks import Check
from juno.inbox import Inbox, Notice

Announcer = Callable[[Notice], None]


class Heartbeat:
    def __init__(
        self,
        checks: list[Check],
        inbox: Inbox,
        schedule_path: str | Path,
        quiet_hours: tuple[int, int] = (22, 8),
        clock: Callable[[], float] = time.time,
        announcer: Announcer | None = None,
        is_paused: Callable[[], bool] | None = None,
    ):
        self.checks = {c.name: c for c in checks}
        self.inbox = inbox
        self.schedule_path = Path(schedule_path)
        self.quiet_start, self.quiet_end = quiet_hours
        self.clock = clock
        self.announcer = announcer
        self.is_paused = is_paused or (lambda: False)  # Tier 6 kill switch plugs in here
        self._next_due: dict[str, float] = self._load_schedule()
        self._running: set[str] = set()  # overlap guard
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._init_schedule()

    # --- schedule persistence (survives restarts) ---
    def _load_schedule(self) -> dict[str, float]:
        if not self.schedule_path.exists():
            return {}
        try:
            data = json.loads(self.schedule_path.read_text(encoding="utf-8"))
            return {k: float(v) for k, v in data.items()}
        except (json.JSONDecodeError, OSError, ValueError):
            return {}

    def _save_schedule(self) -> None:
        self.schedule_path.parent.mkdir(parents=True, exist_ok=True)
        self.schedule_path.write_text(
            json.dumps(self._next_due, indent=2) + "\n", encoding="utf-8"
        )

    def _init_schedule(self) -> None:
        """New checks get a first due of now+interval, so a restart doesn't fire
        everything at once on boot. Persisted dues are kept as-is (resume, don't reset)."""
        now = self.clock()
        changed = False
        for name, check in self.checks.items():
            if name not in self._next_due:
                self._next_due[name] = now + check.interval_seconds
                changed = True
        # Drop schedule entries for checks that no longer exist.
        for stale in [n for n in self._next_due if n not in self.checks]:
            del self._next_due[stale]
            changed = True
        if changed:
            self._save_schedule()

    # --- quiet hours ---
    def is_quiet(self, now: float) -> bool:
        hour = datetime.fromtimestamp(now).hour
        if self.quiet_start == self.quiet_end:
            return False
        if self.quiet_start < self.quiet_end:
            return self.quiet_start <= hour < self.quiet_end
        return hour >= self.quiet_start or hour < self.quiet_end  # wraps past midnight

    def _should_surface(self, notice: Notice, now: float) -> bool:
        if notice.level == "calm":
            return False  # accumulate quietly; never interrupts
        if notice.level == "critical":
            return True  # earns an interruption even at night
        return not self.is_quiet(now)  # interrupt: hold until waking hours

    # --- the core ---
    def tick(self, now: float | None = None) -> list[Notice]:
        """Run all due checks once. Returns notices actively surfaced this tick."""
        if self.is_paused():
            return []  # kill switch (Tier 6): hold all proactive behavior
        now = self.clock() if now is None else now
        surfaced: list[Notice] = []

        for name, check in self.checks.items():
            if not check.enabled or now < self._next_due.get(name, 0):
                continue
            if name in self._running:
                continue  # a slow run is still going — skip, don't stack

            # Reschedule before running so a slow check can't drift or pile up.
            self._next_due[name] = now + check.interval_seconds
            self._save_schedule()

            self._running.add(name)
            try:
                result = check.run()
            except Exception:  # noqa: BLE001 - a broken check must not kill the loop
                result = None
            finally:
                self._running.discard(name)
            if result is None:
                continue

            notice = self.inbox.add(result.text, result.level, name, now)
            if self._should_surface(notice, now) and self.announcer is not None:
                self.announcer(notice)
                self.inbox.mark_seen([notice.id])
                surfaced.append(notice)
            # Otherwise it's held in the inbox for catch-up-on-return.
        return surfaced

    def catch_up(self) -> list[Notice]:
        """Everything held while the user was away. Marks them seen and returns them."""
        held = self.inbox.unseen()
        if held:
            self.inbox.mark_seen([n.id for n in held])
        return held

    # --- threaded runner (laptop-first; relocatable later) ---
    def start(self, tick_seconds: float = 60.0) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()

        def loop():
            while not self._stop.is_set():
                try:
                    self.tick()
                except Exception:  # noqa: BLE001 - keep the heartbeat alive no matter what
                    pass
                self._stop.wait(tick_seconds)

        self._thread = threading.Thread(target=loop, name="juno-heartbeat", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)


def request_approval(
    ask: Callable[[], bool] | None,
    timeout_seconds: float,
    on_timeout_note: Callable[[], None] | None = None,
) -> bool:
    """Ask a human to approve a background action without ever blocking forever.

    If no one is available to answer (`ask is None`) or the answer doesn't arrive within
    the timeout, fall back to the safe default: do nothing, leave a note, keep the loop
    alive. Returns True only on an explicit, in-time yes.
    """
    if ask is None:
        if on_timeout_note:
            on_timeout_note()
        return False

    result: dict[str, bool] = {}
    done = threading.Event()

    def worker():
        try:
            result["v"] = bool(ask())
        finally:
            done.set()

    threading.Thread(target=worker, daemon=True).start()
    if done.wait(timeout_seconds):
        return result.get("v", False)
    if on_timeout_note:
        on_timeout_note()
    return False  # timed out -> safe default
