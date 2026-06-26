"""The rails — the confirmation gate and the kill switch.

The gate sits between the model *choosing* a tool and the tool *running*. Because every
front-end (typed, spoken, heartbeat) funnels tool execution through the same agent core,
one gate covers them all. A tool is consequential if it declares itself so in the
registry OR is named in config's confirm-required list. Consequential tools never run on
assumed permission: the gate states plainly what it intends to do and waits for an
explicit, per-action yes. Approving one action never pre-authorizes the next.

The kill switch pauses all proactive behavior at once (config flag or a flag file) while
the conversation keeps working.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

# A confirmer is asked to approve one action. It returns True only on an explicit yes.
# `None` means "no one is available to ask" (e.g. an unattended heartbeat action), which
# the gate treats as a safe-default no.
Confirmer = Callable[[str, dict[str, Any]], bool] | None


class ConfirmationGate:
    def __init__(self, confirm_required: set[str], confirmer: Confirmer = None, audit=None):
        self._required = set(confirm_required)
        self._confirmer = confirmer
        self._audit = audit

    def is_consequential(self, *, name: str, declared: bool) -> bool:
        """A tool is gated if it declares itself consequential or config requires it."""
        return declared or name in self._required

    def authorize(self, *, name: str, declared: bool, tool_input: dict[str, Any]) -> bool:
        """Return True if the action may run. Records the decision in the audit log."""
        if not self.is_consequential(name=name, declared=declared):
            return True  # read-only actions flow freely

        if self._confirmer is None:
            # Unattended consequential action -> safe default: do nothing, leave a note.
            if self._audit:
                self._audit.confirmation(name, tool_input, approved=False, via="unattended")
            return False

        approved = bool(self._confirmer(name, tool_input))
        if self._audit:
            self._audit.confirmation(name, tool_input, approved=approved, via="user")
        return approved


def describe_action(name: str, tool_input: dict[str, Any]) -> str:
    """A plain-language statement of what's about to happen, for the confirm prompt."""
    if tool_input:
        args = ", ".join(f"{k}={v!r}" for k, v in tool_input.items())
        return f"{name}({args})"
    return f"{name}()"


def is_paused(config) -> bool:
    """The kill switch: true if config says paused or the flag file exists."""
    ks = config.section("killswitch")
    if ks.get("paused", False):
        return True
    flag = ks.get("flag_file", "juno/state/PAUSED")
    return Path(flag).exists()


def set_paused(config, paused: bool) -> None:
    """Toggle the kill switch via its flag file (no code or config edit needed)."""
    flag = Path(config.section("killswitch").get("flag_file", "juno/state/PAUSED"))
    if paused:
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text("paused\n", encoding="utf-8")
    else:
        flag.unlink(missing_ok=True)
