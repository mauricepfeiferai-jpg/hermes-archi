#!/usr/bin/env python3
"""Decision Card with Pydantic validation, repair loop, and fallback chain.
Replaces/extends decision_card.py with structured output guarantees.
"""
import json, re, sys, uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Literal, List, Optional
from pydantic import BaseModel, Field, ValidationError, model_validator

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"
DECISION_DIR = REPO / "control-plane" / "decisions"
DECISION_DIR.mkdir(parents=True, exist_ok=True)

Gate = Literal["GREEN", "YELLOW", "RED"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class DecisionOption(BaseModel):
    label: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=10, max_length=1000)
    gate: Gate


class DecisionCard(BaseModel):
    card_id: str = Field(default_factory=lambda: f"DC_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}")
    goal: str = Field(..., min_length=10, max_length=500)
    options: List[DecisionOption] = Field(..., min_length=2, max_length=5)
    recommendation: str = Field(..., min_length=5, max_length=500)
    risks: List[str] = Field(..., min_length=1, max_length=10)
    evidence: List[str] = Field(default_factory=list, max_length=10)
    time_estimate: str = Field(..., min_length=1, max_length=100)
    cost_estimate: str = Field(..., min_length=1, max_length=100)
    risk_level: RiskLevel
    rollback: str = Field(..., min_length=5, max_length=500)
    review: str = Field(..., min_length=5, max_length=500)
    agent: str = Field(default="Hermes")
    gate: Gate

    @model_validator(mode='after')
    def check_recommendation_and_red_gate(self):
        rec = (self.recommendation or "").lower()
        labels = [o.label.lower() for o in self.options]
        if not any(label in rec for label in labels):
            raise ValueError("recommendation must reference one of the option labels")
        if self.gate == "RED" and not self.risks:
            raise ValueError("RED gate requires at least one risk")
        return self


def render_markdown(card: DecisionCard) -> str:
    options_text = "\n".join(f"{i+1}. **{opt.label}** ({opt.gate}): {opt.description}" for i, opt in enumerate(card.options))
    risks_text = "\n".join(f"- {r}" for r in card.risks) or "- Keine bekannten Risiken"
    evidence_text = "\n".join(f"- {e}" for e in card.evidence) or "- Noch keine Beweise gesammelt"

    return f'''# Decision Card {card.card_id}

## Ziel
{card.goal}

## Optionen
{options_text}

## Empfehlung
{card.recommendation}

## Risiken
{risks_text}

## Beweise
{evidence_text}

## Kosten / Aufwand
- Zeit: {card.time_estimate}
- Geld: {card.cost_estimate}
- Risiko: {card.risk_level}

## Gate
- [ ] GREEN — sofort ausführen
- [ ] YELLOW — mit Korrekturen freigeben
- [x] RED — Maurice muss aktiv entscheiden

## Rollback
{card.rollback}

## Nächste Review
{card.review}

## Vorgeschlagen von
{card.agent}
'''


def save(card: DecisionCard) -> Path:
    path = DECISION_DIR / f"{card.card_id}.md"
    path.write_text(render_markdown(card))
    return path


def _extract_field(text: str, field: str, fallback: str = "") -> str:
    pattern = rf"(?i)###?\s*{re.escape(field)}\s*[:\n](.*?)(?=\n###?\s|$)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return fallback


def _extract_list(text: str, field: str) -> list:
    section = _extract_field(text, field)
    return [re.sub(r"^[-*•]\s*", "", line).strip() for line in section.splitlines() if line.strip().startswith(("-", "*", "•"))]


def repair_parse(raw_text: str, attempt: int = 0) -> DecisionCard:
    """Fallback chain: try strict parse, then extract from markdown, then minimal fallback."""
    try:
        return DecisionCard.model_validate_json(raw_text)
    except (ValidationError, json.JSONDecodeError):
        pass

    try:
        data = json.loads(raw_text)
        return DecisionCard.model_validate(data)
    except (ValidationError, json.JSONDecodeError):
        pass

    # Markdown extraction
    goal = _extract_field(raw_text, "Ziel") or _extract_field(raw_text, "Goal") or "Entscheidung erforderlich"
    recommendation = _extract_field(raw_text, "Empfehlung") or _extract_field(raw_text, "Recommendation") or "Keine Empfehlung"
    rollback = _extract_field(raw_text, "Rollback") or "Nicht definiert"
    review = _extract_field(raw_text, "Nächste Review") or _extract_field(raw_text, "Review") or "Bei nächster Review"
    time_estimate = _extract_field(raw_text, "Zeit") or "Unbekannt"
    cost_estimate = _extract_field(raw_text, "Geld") or _extract_field(raw_text, "Cost") or "$0"
    risk_level = "MEDIUM"
    for lvl in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if lvl.lower() in raw_text.lower():
            risk_level = lvl
            break

    options = []
    opts_section = _extract_field(raw_text, "Optionen") or _extract_field(raw_text, "Options")
    for line in opts_section.splitlines():
        line = re.sub(r"^\d+\.\s*", "", line).strip()
        if line:
            parts = line.split("**")
            if len(parts) >= 3:
                label = parts[1].strip()
                desc = parts[-1].strip()
            else:
                label = line[:60]
                desc = line
            options.append({"label": label, "description": desc, "gate": "RED"})

    if len(options) < 2:
        options = [
            {"label": "Option A", "description": "Empfohlene Vorgehensweise ausführen", "gate": "RED"},
            {"label": "Option B", "description": "Nichts tun / abbrechen", "gate": "GREEN"},
        ]

    risks = _extract_list(raw_text, "Risiken") or _extract_list(raw_text, "Risks") or ["Risiko nicht spezifiziert"]
    evidence = _extract_list(raw_text, "Beweise") or _extract_list(raw_text, "Evidence") or []

    try:
        return DecisionCard(
            goal=goal,
            options=options,
            recommendation=recommendation,
            risks=risks,
            evidence=evidence,
            time_estimate=time_estimate,
            cost_estimate=cost_estimate,
            risk_level=risk_level,  # type: ignore[arg-type]
            rollback=rollback,
            review=review,
            gate="RED",
        )
    except ValidationError as e:
        if attempt > 2:
            raise
        # Minimal fallback
        return DecisionCard(
            goal=goal[:500],
            options=[
                DecisionOption(label="Ja", description="Vorgeschlagene Aktion ausführen", gate="RED"),
                DecisionOption(label="Nein", description="Abbrechen und neu planen", gate="GREEN"),
            ],
            recommendation=recommendation[:500] or "Keine klare Empfehlung",
            risks=["Parsing der Decision Card ist fehlgeschlagen, bitte manuell prüfen"],
            evidence=[],
            time_estimate="Unbekannt",
            cost_estimate="$0",
            risk_level="MEDIUM",
            rollback="Keine automatische Aktion",
            review="Manuelle Review erforderlich",
            gate="RED",
        )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        card = DecisionCard(
            goal="Soll Hermes einen X/Twitter-Post zu aktuellen AI-Agent-Trends verfassen und live veröffentlichen?",
            options=[
                DecisionOption(label="Entwurf speichern", description="Nur Entwurf erstellen, manuell posten", gate="YELLOW"),
                DecisionOption(label="Live veröffentlichen", description="Post direkt auf X veröffentlichen", gate="RED"),
                DecisionOption(label="Nichts tun", description="Keine Aktion, Thema später prüfen", gate="GREEN"),
            ],
            recommendation="Entwurf speichern — Entwurf speichern und Maurice freigeben lassen. RED-Gate verbietet autonome Veröffentlichung.",
            risks=["Öffentliche Wirkung unter echtem Namen", "Reputationsrisiko", "Potenziell falsche Trenddaten im Mock-Modus"],
            evidence=["x_trends.py liefert 24 Items (Mock-Demo-Modus)", "Neural-Bus Event x.trends.discovered"],
            time_estimate="5 Minuten",
            cost_estimate="$0",
            risk_level="MEDIUM",
            rollback="Post löschen, falls noch möglich; ansonsten Korrekturpost",
            review="Nach Veröffentlichung: Engagement + Kritik prüfen",
            agent="Hermes / x_mcp",
            gate="RED",
        )
        path = save(card)
        print(f"Created validated decision card: {path}")
    elif not sys.stdin.isatty():
        raw = sys.stdin.read()
        try:
            card = repair_parse(raw)
        except ValidationError as e:
            print(json.dumps({"error": str(e)}, indent=2, ensure_ascii=False))
            sys.exit(1)
        path = save(card)
        print(f"Created decision card: {path}")
    else:
        print("Usage: python3 decision_card_pydantic.py --sample")
        print("   or: cat raw.md | python3 decision_card_pydantic.py")