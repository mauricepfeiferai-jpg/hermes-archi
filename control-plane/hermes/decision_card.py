#!/usr/bin/env python3
"""Generate a Decision Card for YELLOW/RED gate actions."""
import json, sys, uuid
from pathlib import Path
from datetime import datetime, timezone

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"
DECISION_DIR = REPO / "control-plane" / "decisions"
DECISION_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATE = '''# Decision Card {card_id}

## Ziel
{goal}

## Optionen
1. {option_a}
2. {option_b}
3. Nichts tun

## Empfehlung
{recommendation}

## Risiken
{risk_lines}

## Beweise
{evidence_lines}

## Kosten / Aufwand
- Zeit: {time_estimate}
- Geld: {cost_estimate}
- Risiko: {risk_level}

## Gate
- [ ] GREEN — sofort ausführen
- [ ] YELLOW — mit Korrekturen freigeben
- [x] RED — Maurice muss aktiv entscheiden

## Rollback
{rollback}

## Nächste Review
{review}

## Vorgeschlagen von
{agent}
'''


def generate(goal: str, option_a: str, option_b: str, recommendation: str,
             risks: list, evidence: list, time_estimate: str, cost_estimate: str,
             risk_level: str, rollback: str, review: str, agent: str = "Hermes") -> Path:
    card_id = f"DC_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
    risk_lines = "\n".join(f"- {r}" for r in risks) or "- Keine bekannten Risiken"
    evidence_lines = "\n".join(f"- {e}" for e in evidence) or "- Noch keine Beweise gesammelt"

    content = TEMPLATE.format(
        card_id=card_id,
        goal=goal,
        option_a=option_a,
        option_b=option_b,
        recommendation=recommendation,
        risk_lines=risk_lines,
        evidence_lines=evidence_lines,
        time_estimate=time_estimate,
        cost_estimate=cost_estimate,
        risk_level=risk_level,
        rollback=rollback,
        review=review,
        agent=agent,
    )

    path = DECISION_DIR / f"{card_id}.md"
    path.write_text(content)
    return path


if __name__ == "__main__":
    # Simple CLI: generate from JSON stdin or minimal args
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        path = generate(
            goal="Soll Hermes einen X/Twitter-Post zu aktuellen AI-Agent-Trends verfassen und live veröffentlichen?",
            option_a="Post veröffentlichen mit aktuellen Trends",
            option_b="Nur Entwurf speichern, manuell posten",
            recommendation="Option B — RED-Gate verbietet autonome Veröffentlichung. Entwurf vorbereiten und Maurice freigeben lassen.",
            risks=["Öffentliche Wirkung unter echtem Namen", "Reputationsrisiko", "Potenziell falsche Trenddaten im Mock-Modus"],
            evidence=["x_trends.py liefert 24 Items (Mock-Demo-Modus)", "Neural-Bus Event x.trends.discovered"],
            time_estimate="5 Minuten",
            cost_estimate="$0",
            risk_level="MEDIUM",
            rollback="Post löschen, falls noch möglich; ansonsten Korrekturpost",
            review="Nach Veröffentlichung: Engagement + Kritik prüfen",
            agent="Hermes / x_mcp"
        )
        print(f"Created sample decision card: {path}")
    elif not sys.stdin.isatty():
        data = json.load(sys.stdin)
        path = generate(**data)
        print(f"Created decision card: {path}")
    else:
        print("Usage: python3 decision_card.py --sample")
        print("   or: echo '{...json...}' | python3 decision_card.py")
