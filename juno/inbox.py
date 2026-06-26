"""The inbox — one place where everything the heartbeat surfaces collects.

Quiet by default: most checks produce nothing. What they do produce lands here and is
*held* until the user sees it (catch-up-on-return), never fired into the void. Every
item is dismissible. The store is plain JSON the user can inspect.

Levels:
  - "calm"      — just accumulate; never interrupts.
  - "interrupt" — wants attention; delivered when the user is around and awake.
  - "critical"  — important enough to interrupt even during quiet hours.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

LEVELS = ("calm", "interrupt", "critical")


@dataclass
class Notice:
    id: int
    text: str
    level: str
    created_at: float
    source: str
    seen: bool = False
    dismissed: bool = False


class Inbox:
    """File-backed, dismissible notices held for the user."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._notices: list[Notice] = []
        self._next_id = 1
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        self._notices = [Notice(**d) for d in data if isinstance(d, dict)]
        self._next_id = max((n.id for n in self._notices), default=0) + 1

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump([asdict(n) for n in self._notices], f, indent=2, ensure_ascii=False)
                f.write("\n")
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def add(self, text: str, level: str, source: str, now: float) -> Notice:
        if level not in LEVELS:
            level = "calm"
        notice = Notice(
            id=self._next_id, text=text, level=level, created_at=now, source=source
        )
        self._next_id += 1
        self._notices.append(notice)
        self._save()
        return notice

    def pending(self) -> list[Notice]:
        """Everything not yet dismissed (the calm log the user can glance at)."""
        return [n for n in self._notices if not n.dismissed]

    def unseen(self) -> list[Notice]:
        """Not yet shown to the user and not dismissed — the catch-up-on-return set."""
        return [n for n in self._notices if not n.seen and not n.dismissed]

    def mark_seen(self, ids: list[int]) -> None:
        changed = False
        for n in self._notices:
            if n.id in ids and not n.seen:
                n.seen = True
                changed = True
        if changed:
            self._save()

    def dismiss(self, notice_id: int) -> bool:
        for n in self._notices:
            if n.id == notice_id and not n.dismissed:
                n.dismissed = True
                self._save()
                return True
        return False
