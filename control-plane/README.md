# 🌌 Pfeifer Empire — Control Plane

> **Verfassung:** Jarvis versteht. Hermes organisiert. OpenClaw handelt. Harvey spezialisiert. Memory erinnert. Verifier entscheidet.

**Repo-Pendant zu** `~/Empire/01_Control_Plane/` auf Maurices System.

---

## Die 4 Kern-Agenten

| Agent           | Rolle                       | Port  | Telegram | Code-Pfad                       |
|-----------------|-----------------------------|-------|----------|---------------------------------|
| 🧠 **Jarvis**   | Personal Chief of Staff     | 18791 | Topic 1  | `jarvis/runtime/main.py`        |
| 📡 **Hermes**   | Goal/Kanban/Worker-OS       | 18790 | Topic 2  | `hermes/runtime/main.py`        |
| 🦅 **OpenClaw** | Execution Engine            | 18789 | Topic 3  | `openclaw/runtime/main.py`      |
| ⚖️ **Harvey**   | Legal / Business / Sales    | 18792 | Topic 4  | `harvey/runtime/main.py`        |

---

## Quickstart (lokal)

```bash
# 1. Python deps (use venv)
python3 -m venv .venv && source .venv/bin/activate
pip install -r control-plane/requirements.txt

# 2. Env setup
cp control-plane/.env.example control-plane/.env
# (edit if needed)

# 3. Start Ollama (separately, host network)
ollama serve

# 4. Start all 4 daemons
./control-plane/scripts/start_all.sh

# 5. Health check
./control-plane/scripts/health.sh

# 6. Talk to Jarvis
./control-plane/scripts/demo_chat.sh "Hi Jarvis, was läuft?"

# 7. Stop
./control-plane/scripts/stop_all.sh
```

### Docker (alternative)

```bash
cd control-plane
docker compose up -d
./scripts/health.sh    # works on host loopback (ports are exposed 127.0.0.1)
```

---

## Verzeichnis-Layout

```
control-plane/
├── README.md                           ← du bist hier
├── SYSTEM_INVENTORY.md                 ← alle Repos/Configs/Agenten/Skills
├── CORE_ARCHITECTURE.md                ← Big Picture, Daten-Flow
├── AGENT_ROLES.md                      ← Rollen + Matrix
├── MIGRATION_PLAN.md                   ← Galaxia → Core4 Phasen
├── LEGACY_MAP.md                       ← KEEP/MERGE/ARCHIVE/DELETE
├── GOAL_STANDARD.md                    ← /goal-Format
├── TELEGRAM_TOPICS.md                  ← 4 Topics
├── .env.example                        ← Env-Template
├── requirements.txt                    ← Python deps
├── docker-compose.yaml                 ← Container-Setup
│
├── common/                             ← geteilte Models + Clients
│   ├── models.py                       ← BusMessage, GoalCard, AgentHealth
│   ├── bus_client.py                   ← Hermes-Client für Agents
│   └── ollama.py                       ← Ollama LLM-Wrapper
│
├── jarvis/
│   ├── JARVIS.md  config.json  router.yaml  memory_policy.md
│   └── runtime/
│       ├── main.py                     ← FastAPI on :18791
│       ├── intent.py                   ← router.yaml → Intent matching
│       └── memory.py                   ← SQLite + Ollama embeddings
│
├── hermes/
│   ├── HERMES.md  config.json  BUS.md  goal_engine.yaml  verifier_rules.md
│   └── runtime/
│       ├── main.py                     ← FastAPI on :18790
│       ├── router.py                   ← Capability-based dispatch
│       ├── kg.py                       ← BlackHole-KG (SQLite)
│       ├── goals.py                    ← Goal YAML-Storage
│       └── verifier.py                 ← Done-Check engine
│
├── openclaw/
│   ├── OPENCLAW.md  config.json  skills_index.md  execution_policy.md
│   └── runtime/
│       ├── main.py                     ← FastAPI on :18789
│       └── skills.py                   ← Skill discovery + run-adapter
│
├── harvey/
│   ├── HARVEY.md  config.json  legal_policy.md  business_policy.md
│   └── runtime/
│       ├── main.py                     ← FastAPI on :18792
│       ├── legal.py                    ← LegalReviewer (PDF + Ollama)
│       └── stripe_bridge.py            ← Stripe webhook + HMAC
│
├── shared-memory/  skills/  telegram/  goals/  reports/
│
├── scripts/
│   ├── start_all.sh                    ← bring up all 4
│   ├── stop_all.sh
│   ├── health.sh                       ← check all health endpoints
│   └── demo_chat.sh                    ← smoke-test Jarvis
│
└── tests/
    ├── test_unit.py                    ← models + intent + skills
    └── test_e2e.py                     ← live bus + chat (requires daemons)
```

---

## Bus-Protokoll (Hermes auf :18790)

Alle Inter-Agent-Kommunikation läuft durch Hermes:

```
POST /dispatch    Send a BusMessage
POST /register    Agent self-registration
GET  /agents      List registered + health
GET  /health      Hermes health
POST /goals       Create a Goal-Card
GET  /goals       List goals (filter ?status=...)
GET  /goals/{id}  Goal details
PATCH /goals/{id} Update status (triggers verifier on review)
POST /verify/{id} Run verifier manually
GET  /trace/{id}  Full event-trace of a message or goal
```

Beispiel: User-Anfrage in Jarvis-Chat
```bash
curl -X POST http://127.0.0.1:18791/chat \
  -H "content-type: application/json" \
  -d '{"text": "Schreib mir 5 Tweets zu Ollama", "user_id": "maurice"}'
```

Was dann passiert:
1. Jarvis nimmt User-Text entgegen
2. Lädt Memory-Kontext (letzte 5 Turns + Vector-Hits)
3. Klassifiziert Intent via `router.yaml` → `content_creation`
4. Dispatcht via Hermes an OpenClaw
5. OpenClaw runs `content-engine` Skill (in Phase 2 noch Stub)
6. Result → Jarvis → User
7. Memory schreibt Turn weg

Full Trace einsehbar via `GET /trace/{message_id}`.

---

## Aktueller Status

### Phase 1 — Setup ✅
- Komplette Doku (System-Inventur, Verfassung, Roles, Migration)
- 4-Agent-Strukturen + Configs + Policies

### Phase 2 — MVP Runtime ✅ (heute)
- Hermes Bus-Daemon (Routing, KG-Audit, Goal-Engine, Verifier)
- Jarvis Personal-Orchestrator (Intent-Router, Memory, Ollama)
- OpenClaw Adapter (Skill-Discovery + Stub-Execution)
- Harvey (Legal-Reviewer mit PDF + Stripe-Webhook + Paywall)
- Docker-Compose + Start-Scripts + Tests
- E2E + Unit-Tests

### Phase 3 — Production-Wiring (TODO)
- OpenClaw real-execution Hooks (Node-Bridge zu existing `/openclaw/`)
- CORE Memory Engine als Jarvis-Backend (statt SQLite-Stub)
- Galaxia Vector DB importieren
- MCP-Server für Cursor/Claude Code

### Phase 4 — Telegram Bot (TODO)
- 4 Topics live, Persona-Routing
- Inter-Topic-Handoff
- Stripe-Notifications

### Phase 5 — Galaxia Archive (TODO)
- Friends-Configs nach `/legacy/galaxia/friends/`

---

## Iron Rules (für jeden Agent)

1. Niemand redet direkt mit niemandem — alles über Hermes
2. Jarvis ist Single-Point-of-Contact für Maurice
3. Skills gehören OpenClaw; Legal-Skills gehören Harvey
4. Memory ist Jarvis-only (write); KG ist shared
5. Kein API-Spend — nur Ollama
6. Human-in-the-Loop bei >50€ Spend
7. Hermes verifiziert — kein "done" ohne Done-Check

---

## Was Maurice am Hetzner deployen muss

1. **Python 3.11+** auf Hetzner installiert
2. **Ollama** läuft + alle 6 Modelle gezogen:
   ```bash
   ollama pull qwen3:32b
   ollama pull qwen3-coder
   ollama pull qwen3:14b
   ollama pull deepseek-r1:32b
   ollama pull llama4
   ollama pull nomic-embed-text
   ```
3. **Repo klonen** + Branch checken:
   ```bash
   git clone <url> && cd core
   git checkout claude/export-branches-kYh7h
   ```
4. **Env setzen**: `cp control-plane/.env.example control-plane/.env`
5. **Deps installieren**: `pip install -r control-plane/requirements.txt`
6. **Daemons starten**: `./control-plane/scripts/start_all.sh`
7. **Tests laufen lassen**: `pytest control-plane/tests/ -v`

Für Production: systemd-Units (Phase 3).
