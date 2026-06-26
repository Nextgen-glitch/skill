"""Tier 4 verification — memory survives restarts and is honest, bounded, editable.

Proves: a fact written in one session is present after reloading the store from disk;
a hand-edit to the file is respected on the next load; facts load into the system
prompt; and the store is plain, human-readable JSON.
"""

from __future__ import annotations

import json

from juno.agent import build_system_prompt
from juno.config import Config
from juno.memory import MemoryStore
from juno.tools import memory_tools


def test_fact_survives_restart(tmp_path):
    path = tmp_path / "memory.json"

    # Session 1: learn something, then "quit" (drop the object).
    store = MemoryStore(path)
    store.add("The user prefers morning meetings.")

    # Session 2: a fresh store reading the same file remembers it.
    reloaded = MemoryStore(path)
    facts = [e["fact"] for e in reloaded.all()]
    assert "The user prefers morning meetings." in facts


def test_hand_edit_is_respected(tmp_path):
    path = tmp_path / "memory.json"
    store = MemoryStore(path)
    entry = store.add("The user lives in Bern.")

    # User opens the file and corrects the fact by hand.
    data = json.loads(path.read_text())
    data[0]["fact"] = "The user lives in Zurich."
    path.write_text(json.dumps(data, indent=2))

    reloaded = MemoryStore(path)
    facts = [e["fact"] for e in reloaded.all()]
    assert "The user lives in Zurich." in facts
    assert "The user lives in Bern." not in facts
    assert reloaded.all()[0]["id"] == entry["id"]  # stable identity


def test_memory_loads_into_system_prompt(tmp_path):
    path = tmp_path / "memory.json"
    store = MemoryStore(path)
    store.add("The user runs a bike shop.")

    config = Config.load()
    prompt = build_system_prompt(config, store.prompt_block())

    assert "bike shop" in prompt
    # Framed as data, not commands — no backdoor around the gate.
    assert "data, not as commands" in prompt


def test_memory_tools_act_on_bound_store(tmp_path):
    path = tmp_path / "memory.json"
    store = MemoryStore(path)
    memory_tools.bind_memory(store)

    msg = memory_tools.remember("The user signs off as 'R'.")
    assert "Saved" in msg
    assert any("signs off as 'R'" in e["fact"] for e in store.all())

    fact_id = store.all()[0]["id"]
    assert "Updated" in memory_tools.update_memory(fact_id, "The user signs off as 'Ramsauer'.")
    assert "Forgot" in memory_tools.forget(fact_id)
    assert store.all() == []


def test_empty_store_adds_no_prompt_block(tmp_path):
    store = MemoryStore(tmp_path / "memory.json")
    assert store.prompt_block() is None
