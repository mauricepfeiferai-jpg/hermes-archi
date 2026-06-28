"""Unit tests — no daemons required.

Run with:  pytest control-plane/tests/test_unit.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "jarvis" / "runtime"))
sys.path.insert(0, str(ROOT / "openclaw" / "runtime"))
sys.path.insert(0, str(ROOT / "hermes" / "runtime"))


def test_bus_message_model():
    from common.models import BusMessage, MessageType

    msg = BusMessage.model_validate({
        "from": "test", "to": "openclaw", "type": "task",
        "intent": "content_creation", "payload": {"text": "hi"},
    })
    assert msg.from_ == "test"
    assert msg.type == MessageType.TASK
    j = msg.model_dump(by_alias=True)
    assert j["from"] == "test"


def test_goal_card_default_id():
    from common.models import GoalCard

    g = GoalCard(title="x", owner_agent="openclaw")
    assert g.id.startswith("goal_")
    assert g.status.value == "todo"


def test_intent_router_loads_yaml():
    from intent import IntentRouter

    ir = IntentRouter()
    assert len(ir.intents) > 0
    # greeting should match
    intent = ir.classify("Hi Jarvis")
    assert intent.id in ("greeting", "fallback_conversation")


def test_intent_router_delegates_legal():
    from intent import IntentRouter

    ir = IntentRouter()
    intent = ir.classify("Bitte prüfe diesen Vertrag")
    assert intent.delegate_to == "harvey"


def test_intent_router_delegates_content():
    from intent import IntentRouter

    ir = IntentRouter()
    intent = ir.classify("Schreib mir einen Tweet zu KI")
    assert intent.delegate_to == "openclaw"


def test_skill_registry_discovery():
    from skills import SkillRegistry

    reg = SkillRegistry()
    reg.discover()
    # We may discover 0 if openclaw.json isn't reachable, but the API must work
    caps = reg.capabilities()
    assert "browser" in caps
    assert "skills" in caps


def test_memory_facts_fts(tmp_path, monkeypatch):
    """Imported facts must be keyword-searchable via FTS5."""
    monkeypatch.setenv("JARVIS_MEMORY_DB", str(tmp_path / "mem.db"))
    import importlib
    import memory as memory_mod
    importlib.reload(memory_mod)

    mem = memory_mod.MemoryClient()
    mem.write_fact("Kammertermin Brandi GmbH am 13.05.2026, Vergleich 130K",
                   label="schatzkammer", source="schatzkammer")
    mem.write_fact("Freqtrade Dry-Run Strategie mit RSI und EMA",
                   label="schatzkammer", source="schatzkammer")
    mem.conn.commit()

    hits = mem.search_facts("Brandi Vergleich Kammertermin")
    assert hits, "FTS should find the Brandi fact"
    assert any("Brandi" in h["text"] for h in hits)
    assert mem.search_facts("zzz_nonexistent_token") == []


def test_memory_source_idempotency(tmp_path, monkeypatch):
    monkeypatch.setenv("JARVIS_MEMORY_DB", str(tmp_path / "mem2.db"))
    import importlib
    import memory as memory_mod
    importlib.reload(memory_mod)

    mem = memory_mod.MemoryClient()
    assert not mem.is_source_imported("k1")
    mem.mark_source_imported("k1", 5)
    assert mem.is_source_imported("k1")


def test_skill_run_ollama_unavailable(tmp_path):
    """When Ollama is unreachable, skill run returns a clean fallback (not an exception)."""
    import asyncio
    import os
    os.environ["OLLAMA_URL"] = "http://127.0.0.1:19999"  # nothing running there
    from skills import SkillRegistry

    reg = SkillRegistry()
    reg.discover()
    # Pick any skill (content-engine is always in workspace)
    result = asyncio.run(reg.run("content-engine", {"text": "Schreib einen Tweet über KI"}))
    assert result["status"] in ("done", "ollama_unavailable", "unknown")
    assert "reply" in result


def test_skill_registry_loads_skill_md(tmp_path):
    """SKILL.md is read and used as system prompt material."""
    from skills import SkillRegistry, WORKSPACE

    reg = SkillRegistry()
    reg.discover()
    # At least content-engine should have a SKILL.md in the workspace
    if reg.get("content-engine"):
        md = reg._load_skill_md("content-engine")
        assert len(md) > 10  # not empty


def test_legacy_galaxia_friends_archived():
    """Friends agents must exist in legacy/galaxia/friends/."""
    agents_dir = Path(__file__).resolve().parents[2] / "legacy" / "galaxia" / "friends"
    assert agents_dir.exists(), "legacy/galaxia/friends/ must exist"
    names = {p.name for p in agents_dir.iterdir() if p.is_dir()}
    for agent in ("monica", "chandler", "dwight", "kelly", "pam", "ross", "ryan"):
        assert agent in names, f"{agent} missing from legacy archive"
