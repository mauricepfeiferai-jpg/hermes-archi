#!/usr/bin/env python3
import json, sys
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"
BUS_DIR = REPO / "state" / "neural-bus"
DOP_DIR = REPO / "state" / "dopamine"
LOOP_DIR = REPO / "loop"
OUT_DIR = REPO / "state" / "adaptive-loop-engine"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PATTERN_LIBRARY = {
    "low_morning_dopamine": {
        "trigger": "dopamine.score < homeostasis_threshold at 06:00",
        "suggested_loop": "05-dopamine-rescue",
        "action": "Run a tiny shipping task automatically",
        "rationale": "Biochemical rescue: low dopamine -> small guaranteed win to restart reward circuit."
    },
    "high_research_low_ship": {
        "trigger": "library.entry count > ship.ready count * 3",
        "suggested_loop": "09-researcher-to-spec",
        "action": "Auto-create PRODUCT.md for top discovered repo",
        "rationale": "System ingests knowledge faster than it ships. Convert discovery into product specs."
    },
    "revenue_event": {
        "trigger": "revenue neural bus event",
        "suggested_loop": "30-revenue-celebration",
        "action": "Notify all channels, update dashboard, write GOLD_NUGGET",
        "rationale": "Reinforce the money circuit: every sale must be visible and celebrated."
    },
    "streak_broken": {
        "trigger": "dopamine.streak drops to 0",
        "suggested_loop": "29-streak-rescue",
        "action": "Surface easiest 5-minute ship task to emperor",
        "rationale": "Prevent extinction of shipping habit. Break spiral with trivial success."
    },
    "many_alerts": {
        "trigger": "cto.tech_health alerts >= 2 for 2 days",
        "suggested_loop": "19-health-repair",
        "action": "Open issue, assign cto, schedule repair window",
        "rationale": "Chronic stress signal needs intervention, not more reports."
    }
}

def load_json(path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default

def count_events(days=7):
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    counts = Counter()
    for f in sorted(BUS_DIR.glob("*.json")):
        try:
            ev = json.loads(f.read_text())
            ts = datetime.fromisoformat(ev.get("ts", "").replace("Z", "+00:00"))
            if ts.timestamp() > cutoff:
                counts[ev.get("type", "unknown")] += 1
        except Exception:
            pass
    return counts

def analyze():
    score_state = load_json(DOP_DIR / "score.json", {"score": 0, "streak": 0, "homeostasis_threshold": 5})
    history = load_json(DOP_DIR / "history.json", [])
    lessons = load_json(LOOP_DIR / "lessons.json", [])
    counts = count_events(days=7)

    proposals = []
    current_score = score_state.get("score", 0)
    threshold = score_state.get("homeostasis_threshold", 5)
    streak = score_state.get("streak", 0)

    if current_score < threshold:
        proposals.append({**PATTERN_LIBRARY["low_morning_dopamine"], "confidence": "high"})

    library_count = counts.get("library.entry", 0)
    ship_count = counts.get("engineer.ship.ready", 0)
    if library_count > (ship_count * 3 + 1):
        proposals.append({**PATTERN_LIBRARY["high_research_low_ship"], "confidence": "medium", "ratio": round(library_count / max(ship_count, 1), 2)})

    if counts.get("revenue", 0) > 0:
        proposals.append({**PATTERN_LIBRARY["revenue_event"], "confidence": "high"})

    if streak == 0 and len(history) >= 2 and history[-2].get("streak", 0) > 0:
        proposals.append({**PATTERN_LIBRARY["streak_broken"], "confidence": "high"})

    alert_days = sum(1 for h in history[-7:] if h.get("alerts", 0) >= 2)
    if alert_days >= 2:
        proposals.append({**PATTERN_LIBRARY["many_alerts"], "confidence": "medium"})

    report = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "score": current_score,
        "threshold": threshold,
        "streak": streak,
        "event_counts": dict(counts.most_common(20)),
        "lessons_count": len(lessons),
        "proposals": proposals,
        "next_action": "emperor reviews proposals and approves one for implementation"
    }

    outfile = OUT_DIR / ("report_" + datetime.now().strftime("%Y-%m-%d_%H-%M") + ".json")
    outfile.write_text(json.dumps(report, indent=2))

    event = {
        "ts": report["ts"],
        "type": "adaptive.loop.proposals",
        "source": "adaptive_loop_engine.py",
        "payload": report,
        "recipients": ["emperor", "loop_agent", "openclaw_main"]
    }
    ts = report["ts"].replace(":", "-").replace(".", "-")
    (BUS_DIR / (ts + "_adaptive.loop.proposals.json")).write_text(json.dumps(event, indent=2))

    print("Adaptive Loop Engine:", len(proposals), "proposals")
    for p in proposals:
        print("  -", p["suggested_loop"], ":", p["rationale"])
    return report

if __name__ == "__main__":
    analyze()
