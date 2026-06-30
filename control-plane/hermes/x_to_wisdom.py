#!/usr/bin/env python3
"""X-to-Wisdom Engine: process X posts into system capital.
Reads X URL + text, outputs structured First-Principles analysis.
"""
import json, sys, re
from pathlib import Path
from datetime import datetime, timezone

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"
OUT_DIR = REPO / "state" / "x-to-wisdom"
BUS_DIR = REPO / "state" / "neural-bus"


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def slugify(text: str) -> str:
    s = re.sub(r'[^\w\s-]', '', text.lower())
    s = re.sub(r'[-\s]+', '-', s)
    return s[:50].strip('-')


def emit_event(payload: dict):
    BUS_DIR.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": now_iso(),
        "type": "x.to_wisdom.processed",
        "source": "x_to_wisdom.py",
        "payload": payload,
        "recipients": ["emperor", "researcher", "writer"]
    }
    ts = now_iso().replace(":", "-").replace(".", "-")
    (BUS_DIR / f"{ts}_x.to_wisdom.processed.json").write_text(json.dumps(event, indent=2))


def process(url: str, text: str, context: str = "") -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Simple keyword-based signal/hype heuristics
    hype_words = ["revolution", "game changer", "10x", "100x", "must have", "everyone is using", "fomo", "urgent"]
    signal_words = ["because", "data shows", "measured", "tested", "benchmark", "study", "example", "observed"]

    t_lower = text.lower()
    hype_score = sum(1 for w in hype_words if w in t_lower)
    signal_score = sum(1 for w in signal_words if w in t_lower)

    # Determine primary topic
    topics = {
        "ai agents": ["ai agent", "agent", "claude code", "hermes", "mcp"],
        "content": ["post", "tweet", "content", "viral", "thread"],
        "business": ["money", "revenue", "product", "customer", "sell"],
        "legal": ["law", "legal", "contract", "rechts"],
        "health": ["health", "weight", "sleep", "fitness"],
        "loops": ["loop", "workflow", "automation"],
    }
    topic_scores = {topic: sum(1 for w in words if w in t_lower) for topic, words in topics.items()}
    primary_topic = max(topic_scores, key=topic_scores.get) if max(topic_scores.values()) > 0 else "general"

    # Extract a simple "claim" from first sentence
    claim = text.split('.')[0][:120] + ("..." if len(text.split('.')[0]) > 120 else "")

    # Maurice relevance heuristic
    maurice_relevance = "high" if any(w in t_lower for w in ["agent", "loop", "workflow", "money", "product", "legal", "bma"]) else "medium"

    # Generate output structure
    result = {
        "generated_at": now_iso(),
        "source_url": url,
        "context": context,
        "primary_topic": primary_topic,
        "claim": claim,
        "assumptions": [
            "Der Autor spricht aus eigener Erfahrung oder beobachteter Praxis.",
            "Die empfohlene Methode ist auf Maurice' Kontext übertragbar.",
            "Die Kosten/Zeit für Umsetzung sind vertretbar."
        ],
        "first_principles": [
            "Aufmerksamkeit ist begrenzt — nur skalierbare Systeme überleben.",
            "Feedback ohne Systemlernen ist verschwendet.",
            "Verantwortung bleibt beim Menschen, Arbeit geht an die Maschine."
        ],
        "hype_signals": {
            "hype_score": hype_score,
            "signal_score": signal_score,
            "assessment": "high_hype" if hype_score > signal_score else "balanced" if hype_score == signal_score else "low_hype"
        },
        "maurice_relevance": maurice_relevance,
        "usable_for": [
            "HERMES_RULES.md Regel-Update" if "loop" in t_lower or "agent" in t_lower else None,
            "Content Seed für X/LinkedIn" if maurice_relevance == "high" else None,
            "Product Signal" if "product" in t_lower or "money" in t_lower else None,
            "Loop Upgrade" if "loop" in t_lower or "workflow" in t_lower else None,
        ],
        "score": {
            "truth": 7,
            "novelty": 6,
            "leverage": 8 if maurice_relevance == "high" else 5,
            "maurice_fit": 8 if maurice_relevance == "high" else 5,
            "system_fit": 7 if "loop" in t_lower or "agent" in t_lower else 4,
            "business_fit": 6 if "money" in t_lower or "product" in t_lower or "sell" in t_lower else 3,
            "content_fit": 7 if maurice_relevance == "high" else 4,
            "risk": 3,
            "actionability": 7 if maurice_relevance == "high" else 4,
            "compound_potential": 8 if "loop" in t_lower or "system" in t_lower else 5,
        },
        "next_action": "Review ausgeben, Maurice prüft Ableitung, Learning Agent extrahiert Regel.",
        "system_rule": None,
        "status": "pending_review"
    }

    # Compute average score
    scores = [v for v in result["score"].values() if isinstance(v, (int, float))]
    result["average_score"] = round(sum(scores) / len(scores), 1) if scores else 0

    # Determine status
    if result["average_score"] >= 9:
        result["status"] = "candidate_rule"
    elif result["average_score"] >= 8:
        result["status"] = "loop_experiment"
    elif result["average_score"] >= 7:
        result["status"] = "knowledge_card"
    elif result["average_score"] >= 6:
        result["status"] = "archive"
    else:
        result["status"] = "reject"

    # Clean up None values
    result["usable_for"] = [x for x in result["usable_for"] if x]

    # Save output
    slug = slugify(claim) or "x-post"
    outfile = OUT_DIR / f"{now_iso()[:10]}_{slug}.json"
    outfile.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    emit_event({
        "file": str(outfile),
        "url": url,
        "topic": primary_topic,
        "avg_score": result["average_score"],
        "status": result["status"]
    })

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: x_to_wisdom.py <x-url> [context]")
        print("   or: echo 'post text' | x_to_wisdom.py <x-url> [context]")
        sys.exit(1)

    url = sys.argv[1]
    context = sys.argv[2] if len(sys.argv) > 2 else ""

    if not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print("Please provide post text via stdin.")
        sys.exit(1)

    result = process(url, text, context)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
