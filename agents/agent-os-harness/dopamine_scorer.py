#!/usr/bin/env python3
import json, sys
from pathlib import Path
from datetime import datetime, timezone

def score(repo_str, yesterday, today):
    repo = Path(repo_str)
    bus_dir = repo / "state" / "neural-bus"
    dopamine_dir = repo / "state" / "dopamine"
    dopamine_dir.mkdir(parents=True, exist_ok=True)

    score_file = dopamine_dir / "score.json"
    history_file = dopamine_dir / "history.json"

    score_state = {"score": 0.0, "streak": 0, "last_updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}
    if score_file.exists():
        score_state = json.loads(score_file.read_text())

    score_state["score"] = round(score_state.get("score", 0.0) * 0.95, 2)

    cutoff = datetime.now(timezone.utc).timestamp() - 24 * 3600
    events = []
    for f in sorted(bus_dir.glob("*.json")):
        try:
            ev = json.loads(f.read_text())
            ts = datetime.fromisoformat(ev.get("ts", "").replace("Z", "+00:00"))
            if ts.timestamp() > cutoff:
                events.append(ev)
        except Exception:
            pass

    breakdown = []
    delta = 0.0
    for ev in events:
        etype = ev.get("type", "")
        payload = ev.get("payload", {})
        d = 0.0
        if etype == "code.completed":
            d += int(payload.get("files", 0) or 0) * 0.1
            d += int(payload.get("tests_passed", 0) or 0) * 2
            d += int(payload.get("commits", 0) or 0) * 1
            d += int(payload.get("merged_prs", 0) or 0) * 5
        elif etype == "skill.created":
            d += 10
        elif etype == "library.entry":
            d += min(int(payload.get("items", 0) or 0) * 0.05, 5)
        elif etype == "revenue":
            d += float(payload.get("amount", 0) or 0) * 50
        elif etype == "agent.dispatch.completed":
            d += 0.5
        elif etype == "ceo.morning_queue":
            d += 1
        elif etype == "cto.tech_health" and len(payload.get("alerts", [])) == 0:
            d += 2
        elif etype == "engineer.ship.ready":
            d += len(payload.get("ship_candidates", [])) * 2
        elif etype == "ops.backup.completed":
            d += 1
        elif etype == "loop.review.completed":
            d += 0.5
        elif etype == "loop.improvement.suggested":
            d += 1
        elif etype == "dopamine.score.updated":
            continue
        else:
            d += 0.1
        delta += d
        breakdown.append({"type": etype, "delta": round(d, 2), "source": ev.get("source", "")})

    score_state["score"] = round(score_state["score"] + delta, 2)
    score_state["last_delta"] = round(delta, 2)
    score_state["last_event"] = "dopamine.daily_score"
    score_state["last_updated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    if delta >= 5:
        score_state["streak"] = score_state.get("streak", 0) + 1
    else:
        score_state["streak"] = 0

    score_state["homeostasis_threshold"] = round(max(5, score_state["score"] * 0.1), 2)

    score_file.write_text(json.dumps(score_state, indent=2))

    history = []
    if history_file.exists():
        history = json.loads(history_file.read_text())
    history.append({
        "ts": score_state["last_updated"],
        "date": today,
        "delta": round(delta, 2),
        "score": score_state["score"],
        "streak": score_state["streak"],
        "threshold": score_state["homeostasis_threshold"],
        "breakdown": breakdown,
    })
    history_file.write_text(json.dumps(history[-365:], indent=2))

    bus_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    event = {
        "ts": now.isoformat().replace("+00:00", "Z"),
        "type": "dopamine.score.updated",
        "source": "24-dopamine-score.sh",
        "payload": score_state,
        "recipients": ["emperor", "openclaw_main", "dashboard", "loop_agent"]
    }
    ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
    (bus_dir / f"{ts}_dopamine.score.updated.json").write_text(json.dumps(event, indent=2))
    print("Dopamine score:", score_state["score"], "(+" + str(round(delta, 2)) + "), streak:", score_state["streak"], "threshold:", score_state["homeostasis_threshold"])

if __name__ == "__main__":
    score(sys.argv[1], sys.argv[2], sys.argv[3])
