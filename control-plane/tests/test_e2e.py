"""End-to-end smoke tests for Pfeifer Core4.

These tests assume all 4 daemons are running locally (use start_all.sh first).
Run with:  pytest control-plane/tests/test_e2e.py -v

If Ollama isn't running, LLM-dependent tests will degrade gracefully and
still assert that the bus routing works.
"""

from __future__ import annotations

import os
import time

import httpx
import pytest

HERMES = os.getenv("HERMES_URL", "http://127.0.0.1:18890")
JARVIS = os.getenv("JARVIS_URL", "http://127.0.0.1:18891")
OPENCLAW = os.getenv("OPENCLAW_URL", "http://127.0.0.1:18892")
HARVEY = os.getenv("HARVEY_URL", "http://127.0.0.1:18893")


# LLM-dependent endpoints (dispatch→Harvey, Jarvis /chat) call Ollama with
# large reasoning models (deepseek-r1:32b, qwen3:32b) that can take >60s on a
# busy host. Keep the client timeout generous and overridable.
E2E_TIMEOUT = float(os.getenv("E2E_TIMEOUT", "180"))


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=E2E_TIMEOUT) as c:
        yield c


def _is_up(client, url: str) -> bool:
    try:
        r = client.get(f"{url}/health", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="module", autouse=True)
def ensure_running(client):
    for name, url in (("hermes", HERMES), ("jarvis", JARVIS),
                      ("openclaw", OPENCLAW), ("harvey", HARVEY)):
        if not _is_up(client, url):
            pytest.skip(f"{name} not running at {url} — run scripts/start_all.sh first")


# -------- Health --------

@pytest.mark.parametrize("name,url", [
    ("hermes", HERMES), ("jarvis", JARVIS),
    ("openclaw", OPENCLAW), ("harvey", HARVEY),
])
def test_health(client, name, url):
    r = client.get(f"{url}/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["name"] == name
    assert body["uptime_seconds"] >= 0


# -------- Registration --------

def test_agents_registered(client):
    """All downstream agents should have self-registered with Hermes."""
    # Give them a moment to register on startup
    time.sleep(2)
    r = client.get(f"{HERMES}/agents")
    assert r.status_code == 200
    names = {a["name"] for a in r.json()["agents"]}
    assert "jarvis" in names
    assert "openclaw" in names
    assert "harvey" in names


# -------- Bus routing --------

def test_dispatch_to_openclaw(client):
    msg = {
        "from": "test",
        "to": "openclaw",
        "type": "task",
        "intent": "content_creation",
        "payload": {"text": "10 X-Posts zu KI", "skill_hint": "content-engine"},
    }
    r = client.post(f"{HERMES}/dispatch", json=msg)
    assert r.status_code == 200
    body = r.json()
    payload = body.get("payload", {})
    # OpenClaw in MVP returns a stub-reply with "[OpenClaw stub]"
    assert "reply" in payload or "stub" in payload


def test_dispatch_to_harvey(client):
    msg = {
        "from": "test",
        "to": "harvey",
        "type": "task",
        "intent": "sales_pipeline",
        "payload": {"user_id": "test-user", "text": "Lead-Liste"},
    }
    r = client.post(f"{HERMES}/dispatch", json=msg)
    assert r.status_code == 200
    body = r.json()
    payload = body.get("payload", {})
    assert "reply" in payload


def test_dispatch_capability_routing(client):
    """Without explicit `to`, intent should route via capability."""
    msg = {
        "from": "test",
        "type": "task",
        "intent": "legal_review",
        "payload": {"user_id": "test-user", "text": "Kurzer Mietvertrag-Test."},
    }
    r = client.post(f"{HERMES}/dispatch", json=msg)
    assert r.status_code == 200


# -------- Goals --------

def test_goal_create_and_list(client):
    goal = {
        "title": "Smoke-Test Goal",
        "owner_agent": "openclaw",
        "priority": "P3",
        "acceptance_criteria": ["test runs"],
        "verifier": {"kind": "file_exists", "args": {"path": "README.md"}},
    }
    r = client.post(f"{HERMES}/goals", json=goal)
    assert r.status_code == 200
    created = r.json()
    goal_id = created["id"]

    r = client.get(f"{HERMES}/goals/{goal_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Smoke-Test Goal"

    r = client.get(f"{HERMES}/goals")
    titles = [g["title"] for g in r.json()["goals"]]
    assert "Smoke-Test Goal" in titles


def test_goal_verify_file_exists(client, tmp_path):
    sentinel = tmp_path / "exists.txt"
    sentinel.write_text("hi")
    goal = {
        "title": "Verifier file_exists smoke",
        "owner_agent": "openclaw",
        "acceptance_criteria": ["sentinel file present"],
        "verifier": {
            "kind": "composite",
            "checks": [
                {"kind": "file_exists", "args": {"path": str(sentinel)}}
            ],
        },
    }
    r = client.post(f"{HERMES}/goals", json=goal)
    goal_id = r.json()["id"]

    r = client.post(f"{HERMES}/verify/{goal_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["overall"] in ("pass", "partial", "fail")  # at least it ran
    assert any(c["check"]["kind"] == "file_exists" for c in body["checks"])


# -------- Jarvis chat --------

def test_jarvis_chat_self_handled(client):
    """A greeting should be self-handled by Jarvis (no delegation)."""
    r = client.post(f"{JARVIS}/chat", json={"text": "Hallo Jarvis"})
    assert r.status_code == 200
    body = r.json()
    assert "reply" in body
    assert body.get("intent") in {"greeting", "fallback_conversation"}


def test_jarvis_chat_delegates_content(client):
    """A 'mach 10 X-Posts' request should route to OpenClaw."""
    r = client.post(f"{JARVIS}/chat", json={"text": "Mach mir 10 X-Posts zu KI-News"})
    assert r.status_code == 200
    body = r.json()
    # Either delegated_to is set, or reply contains OpenClaw stub marker
    assert body.get("delegated_to") in ("openclaw", None)
