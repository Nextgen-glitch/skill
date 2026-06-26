"""Calendar tools.

Tier 2 ships the read-only lookup on a local stub so the loop is easy to verify.
The real Google Calendar service is swapped in behind this same seam later; the
consequential `create_event` / `delete_event` tools land then, gated by Tier 6.
"""

from __future__ import annotations

from juno.tools.registry import Param, tool

# --- stub data (replaced by the real calendar service later) ---------------------
_STUB_EVENTS: dict[str, list[str]] = {
    "today": [
        "09:30  Standup",
        "13:00  Lunch with a supplier",
        "16:00  Follow up on outreach replies",
    ],
    "tomorrow": [
        "11:00  Demo call with a prospect",
    ],
}


@tool(
    name="list_calendar_events",
    description=(
        "Look up the events on the user's calendar for a given day. Use this whenever "
        "the user asks what's on their schedule, what their day looks like, or whether "
        "they're free. Read-only."
    ),
    parameters={
        "day": Param(
            type="string",
            description="The day to look up, e.g. 'today' or 'tomorrow'.",
            required=False,
            default="today",
        ),
    },
    consequential=False,
)
def list_calendar_events(day: str = "today") -> str:
    key = day.strip().lower()
    events = _STUB_EVENTS.get(key)
    if events is None:
        return f"No events found for '{day}'."
    if not events:
        return f"Nothing on the calendar {key}."
    lines = "\n".join(f"  - {e}" for e in events)
    return f"Events for {key}:\n{lines}"
