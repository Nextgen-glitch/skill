"""Memory tools — let the assistant manage its own long-term notes.

These operate on a MemoryStore bound at startup. They are the assistant's own
housekeeping (saving and correcting durable preferences/identities/decisions), not
actions on the user's external data, so they are not consequential — the Tier 6 gate is
for sending, spending, deleting the user's data, and changing settings.
"""

from __future__ import annotations

from juno.memory import MemoryStore
from juno.tools.registry import Param, tool

# Bound at startup by main/build. Until then the tools explain they aren't ready.
_STORE: MemoryStore | None = None


def bind_memory(store: MemoryStore) -> None:
    global _STORE
    _STORE = store


@tool(
    name="remember",
    description=(
        "Save one durable fact about the user or their world — a preference, an "
        "identity, a decision worth recalling next time (e.g. 'prefers morning "
        "meetings'). Use for things that should outlast this conversation, not passing "
        "chatter. Write it as a single plain statement."
    ),
    parameters={"fact": Param("string", "The single fact to remember, as a statement.")},
    consequential=False,
)
def remember(fact: str) -> str:
    if _STORE is None:
        return "(memory isn't available right now)"
    entry = _STORE.add(fact)
    return f"Saved as memory #{entry['id']}: {entry['fact']}"


@tool(
    name="update_memory",
    description=(
        "Correct or replace an existing remembered fact, identified by its number. Use "
        "when something you saved is now stale or wrong."
    ),
    parameters={
        "fact_id": Param("integer", "The number of the memory to change."),
        "fact": Param("string", "The corrected statement."),
    },
    consequential=False,
)
def update_memory(fact_id: int, fact: str) -> str:
    if _STORE is None:
        return "(memory isn't available right now)"
    if _STORE.update(int(fact_id), fact):
        return f"Updated memory #{fact_id}."
    return f"(no memory numbered {fact_id})"


@tool(
    name="forget",
    description=(
        "Remove a remembered fact by its number, when it's no longer true or the user "
        "asks you to forget it."
    ),
    parameters={"fact_id": Param("integer", "The number of the memory to remove.")},
    consequential=False,
)
def forget(fact_id: int) -> str:
    if _STORE is None:
        return "(memory isn't available right now)"
    if _STORE.remove(int(fact_id)):
        return f"Forgot memory #{fact_id}."
    return f"(no memory numbered {fact_id})"
