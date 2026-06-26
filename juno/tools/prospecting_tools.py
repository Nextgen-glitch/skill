"""Prospecting tools.

Tier 2 ships a read-only business search on a local stub so the loop is easy to verify.
The real Vibe Prospecting service is swapped in behind this same seam later. Note that
*enrichment* (paid) is a consequential action and lands gated by Tier 6 — search itself
stays read-only.
"""

from __future__ import annotations

from juno.tools.registry import Param, tool

# --- stub data (replaced by the real prospecting service later) ------------------
_STUB_BUSINESSES = [
    ("Alpine Cycle Studio", "boutique bike fitting and indoor cycling"),
    ("Summit Wheelworks", "mountain bike service and custom builds"),
    ("Lakeside E-Bike Co.", "e-bike sales and guided tours"),
    ("Cobble & Chain Cafe", "cyclist cafe and weekend group rides"),
    ("Velocity Components", "wholesale drivetrain and brake parts"),
]


@tool(
    name="search_businesses",
    description=(
        "Find businesses matching a niche the user describes, optionally in a location. "
        "Use this when the user wants prospects or leads to reach out to. Returns names "
        "and a one-line description for each. Read-only — it does not contact anyone or "
        "spend money."
    ),
    parameters={
        "niche": Param(
            type="string",
            description="The kind of business to find, e.g. 'bike shops' or 'cycling cafes'.",
        ),
        "location": Param(
            type="string",
            description="Optional area to focus on, e.g. 'Zurich' or 'near me'.",
            required=False,
        ),
        "limit": Param(
            type="integer",
            description="Maximum number of results to return (default 5).",
            required=False,
            default=5,
        ),
    },
    consequential=False,
)
def search_businesses(niche: str, location: str | None = None, limit: int = 5) -> str:
    results = _STUB_BUSINESSES[: max(1, min(limit, len(_STUB_BUSINESSES)))]
    where = f" in {location}" if location else ""
    lines = "\n".join(f"  - {name} — {desc}" for name, desc in results)
    return f"Found {len(results)} business(es) for '{niche}'{where}:\n{lines}"
