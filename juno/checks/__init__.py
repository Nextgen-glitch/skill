"""Scheduled checks — each a small, self-contained unit the heartbeat runs.

A check declares how often it runs and, when it runs, decides whether anything is worth
surfacing. Returning None means "nothing to report" — which is the common case, because
the heartbeat is quiet by default. What to check and how often lives in config.toml, not
in code, so tuning a threshold or interval is a one-line edit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class CheckResult:
    """What a check wants surfaced. `level` is one of calm / interrupt / critical."""

    text: str
    level: str = "interrupt"


@dataclass
class Check:
    name: str
    interval_seconds: int
    run: Callable[[], CheckResult | None]
    enabled: bool = True


# name -> factory(check_config) -> Check. Tool/check modules register here.
CHECK_FACTORIES: dict[str, Callable[[dict], Check]] = {}


def register_check(name: str):
    def decorate(factory: Callable[[dict], Check]):
        CHECK_FACTORIES[name] = factory
        return factory

    return decorate


def build_checks(config) -> list[Check]:
    """Build the enabled checks listed under [[heartbeat.checks]] in config."""
    from juno.checks import trigger_watch  # noqa: F401 - registers its factory

    checks: list[Check] = []
    for entry in config.section("heartbeat").get("checks", []):
        name = entry.get("name")
        factory = CHECK_FACTORIES.get(name)
        if factory is None or not entry.get("enabled", True):
            continue
        checks.append(factory(entry))
    return checks
