"""A visible audit trail + a running cost tally.

Every consequential decision, tool run, and model call appends one JSON line to a plain
log the user can read. The cost tally accumulates token usage (and an optional dollar
estimate) so a runaway loop is visible immediately rather than after the bill arrives.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class CostTally:
    """Cumulative token usage, with an optional dollar estimate from config rates."""

    input_per_mtok: float | None = None
    output_per_mtok: float | None = None
    input_tokens: int = 0
    output_tokens: int = 0

    def add(self, input_tokens: int, output_tokens: int) -> None:
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    @property
    def dollars(self) -> float | None:
        if self.input_per_mtok is None or self.output_per_mtok is None:
            return None
        return (
            self.input_tokens / 1_000_000 * self.input_per_mtok
            + self.output_tokens / 1_000_000 * self.output_per_mtok
        )

    def summary(self) -> str:
        base = f"{self.input_tokens} in / {self.output_tokens} out tokens"
        d = self.dollars
        return f"{base} (~${d:.4f})" if d is not None else base


class AuditLog:
    """Append-only JSONL log + an in-memory cost tally."""

    def __init__(self, path: str | Path, tally: CostTally | None = None):
        self.path = Path(path)
        self.tally = tally or CostTally()

    def _write(self, event: dict[str, Any]) -> None:
        event = {"ts": datetime.now(timezone.utc).isoformat(), **event}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    # --- the things worth recording ---
    def tool(self, name: str, tool_input: dict[str, Any], status: str, result: str) -> None:
        """status: 'ran' | 'denied' | 'auto'. Result is truncated to keep the log legible."""
        self._write(
            {
                "kind": "tool",
                "name": name,
                "input": tool_input,
                "status": status,
                "result": result[:500],
            }
        )

    def confirmation(self, name: str, tool_input: dict[str, Any], approved: bool, via: str) -> None:
        self._write(
            {
                "kind": "confirmation",
                "name": name,
                "input": tool_input,
                "approved": approved,
                "via": via,  # 'user' | 'timeout' | 'unattended'
            }
        )

    def model(self, model: str, input_tokens: int, output_tokens: int) -> None:
        self.tally.add(input_tokens, output_tokens)
        self._write(
            {
                "kind": "model",
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cumulative": self.tally.summary(),
            }
        )

    def note(self, message: str, **extra: Any) -> None:
        self._write({"kind": "note", "message": message, **extra})


def build_audit(config) -> AuditLog:
    """Construct the audit log + cost tally from config (pricing optional)."""
    safety = config.section("safety")
    pricing = config.section("pricing")
    tally = CostTally(
        input_per_mtok=pricing.get("input_per_mtok"),
        output_per_mtok=pricing.get("output_per_mtok"),
    )
    return AuditLog(safety.get("audit_log_path", "logs/audit.jsonl"), tally=tally)
