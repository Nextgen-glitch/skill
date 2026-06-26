"""Tier 5 verification — proactive, quiet by default.

Proves: a due check surfaces once; calm items stay in the inbox without interrupting;
items are held for catch-up when no interface is attached; quiet hours hold interrupts
but not critical; the schedule resumes after a restart instead of refiring; overlapping
runs are skipped; notices are dismissible; and a background approval never blocks.
"""

from __future__ import annotations

from datetime import datetime

from juno.checks import Check, CheckResult
from juno.heartbeat import Heartbeat, request_approval
from juno.inbox import Inbox


def _clock(value: list[float]):
    return lambda: value[0]


def _epoch_at_hour(hour: int) -> float:
    # A concrete local timestamp at a given hour, so quiet-hours logic is deterministic.
    return datetime(2026, 6, 26, hour, 0, 0).timestamp()


def _check(name, result_seq, interval=5):
    """A check that returns successive results from result_seq on each run."""
    seq = list(result_seq)

    def run():
        return seq.pop(0) if seq else None

    return Check(name=name, interval_seconds=interval, run=run)


def test_due_check_surfaces_once(tmp_path):
    now = [_epoch_at_hour(10)]  # daytime
    inbox = Inbox(tmp_path / "inbox.json")
    surfaced_log = []
    hb = Heartbeat(
        checks=[_check("c", [CheckResult("ping!", "interrupt"), None])],
        inbox=inbox,
        schedule_path=tmp_path / "sched.json",
        clock=_clock(now),
        announcer=surfaced_log.append,
    )

    # First tick: not yet due (first due is now+interval). Nothing fires.
    assert hb.tick() == []
    # Advance past the interval: it fires exactly once.
    now[0] += 6
    surfaced = hb.tick()
    assert len(surfaced) == 1 and surfaced[0].text == "ping!"
    # Tick again immediately: not due, and the result is consumed — silence.
    assert hb.tick() == []


def test_calm_items_do_not_interrupt_but_are_logged(tmp_path):
    now = [_epoch_at_hour(10)]
    inbox = Inbox(tmp_path / "inbox.json")
    surfaced_log = []
    hb = Heartbeat(
        checks=[_check("c", [CheckResult("fyi", "calm")])],
        inbox=inbox,
        schedule_path=tmp_path / "sched.json",
        clock=_clock(now),
        announcer=surfaced_log.append,
    )
    now[0] += 6
    assert hb.tick() == []  # calm never interrupts
    assert [n.text for n in inbox.pending()] == ["fyi"]  # but it is held to glance at


def test_quiet_hours_hold_interrupt_but_not_critical(tmp_path):
    night = [_epoch_at_hour(2)]  # inside default quiet hours (22–8)
    inbox = Inbox(tmp_path / "inbox.json")
    surfaced_log = []
    hb = Heartbeat(
        checks=[
            _check("soft", [CheckResult("soft news", "interrupt")]),
            _check("loud", [CheckResult("ALARM", "critical")]),
        ],
        inbox=inbox,
        schedule_path=tmp_path / "sched.json",
        quiet_hours=(22, 8),
        clock=_clock(night),
        announcer=surfaced_log.append,
    )
    night[0] += 6
    surfaced = hb.tick()
    texts = [n.text for n in surfaced]
    assert "ALARM" in texts  # critical breaks through
    assert "soft news" not in texts  # interrupt is held until morning
    # The held interrupt is still available to catch up on later.
    assert any(n.text == "soft news" for n in inbox.unseen())


def test_catch_up_returns_held_items_once(tmp_path):
    now = [_epoch_at_hour(10)]
    inbox = Inbox(tmp_path / "inbox.json")
    # No announcer attached -> nothing is actively surfaced; everything is held.
    hb = Heartbeat(
        checks=[_check("c", [CheckResult("missed you", "interrupt")])],
        inbox=inbox,
        schedule_path=tmp_path / "sched.json",
        clock=_clock(now),
        announcer=None,
    )
    now[0] += 6
    hb.tick()
    caught = hb.catch_up()
    assert [n.text for n in caught] == ["missed you"]
    # Seen now — not shown again next time.
    assert hb.catch_up() == []


def test_schedule_resumes_after_restart(tmp_path):
    now = [_epoch_at_hour(10)]
    sched = tmp_path / "sched.json"
    inbox = Inbox(tmp_path / "inbox.json")

    hb1 = Heartbeat([_check("c", [])], inbox, sched, clock=_clock(now))
    first_due = hb1._next_due["c"]

    # "Restart": a brand-new Heartbeat reading the same schedule file.
    hb2 = Heartbeat([_check("c", [])], inbox, sched, clock=_clock(now))
    assert hb2._next_due["c"] == first_due  # resumed, not reset to now


def test_overlapping_runs_are_skipped(tmp_path):
    now = [_epoch_at_hour(10)]
    inbox = Inbox(tmp_path / "inbox.json")
    runs = []

    hb = Heartbeat([], inbox, tmp_path / "sched.json", clock=_clock(now))

    def slow_run():
        runs.append("start")
        # Simulate the next tick arriving mid-run by re-entering tick().
        if len(runs) == 1:
            now[0] += 6
            hb.tick()  # should skip 'c' because it's still running
        return None

    hb.checks = {"c": Check("c", 5, slow_run)}
    hb._next_due["c"] = now[0]  # make it due now
    hb.tick()
    assert runs == ["start"]  # the re-entrant tick did not start a second run


def test_dismiss_clears_a_notice(tmp_path):
    inbox = Inbox(tmp_path / "inbox.json")
    n = inbox.add("clutter", "calm", "c", now=_epoch_at_hour(10))
    assert inbox.dismiss(n.id) is True
    assert inbox.pending() == []
    assert inbox.dismiss(n.id) is False  # already gone


def test_approval_never_blocks_forever():
    notes = []
    # Unattended: no one to ask -> safe default (do nothing), with a note left.
    assert request_approval(None, timeout_seconds=1, on_timeout_note=lambda: notes.append("x")) is False
    assert notes == ["x"]
    # An explicit, in-time yes is honored.
    assert request_approval(lambda: True, timeout_seconds=1) is True
