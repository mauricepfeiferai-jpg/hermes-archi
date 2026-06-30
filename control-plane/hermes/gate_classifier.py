#!/usr/bin/env python3
"""Classify a planned action as GREEN, YELLOW or RED based on HERMES_RULES."""
import re, sys, json

RED_PATTERNS = [
    r"\b(überweis|zahlen|bezahlen|payment|transfer|send money)\w*\b",
    r"\b(unterschreib|vertrag|rechtlich bindend|legal agreement)\w*\b",
    r"\b(lösch|delet|rm -rf|drop table)\w*\b",
    r"\b(deploy\w*\s+(?:nach\s+)?produktion|merge\w*\s+main|push\w*\s+main)\b",
    r"\b(post|tweet|veröffentlich|publish|live\s*schalten)\w*\b",
    r"\b(passwort|secret|api key|credential)\w*\b",
    r"\b(kundendaten|customer data).*senden\b",
    r"\b(geld|money|euro|dollar).{0,30}\b(\d{3,}|viel|groß|hoch)\b",
]

YELLOW_PATTERNS = [
    r"\b(pr|pull request|e-mail|email|entwurf|draft)\b",
    r"\b(kosten|cost|preis|price).{0,30}\b([5-9]|\d{2,})\b",
    r"\b(dependency|api|service).{0,20}(neu|new|add|hinzufügen)\b",
    r"\b(config|configuration|einstellung).{0,20}(änder|change|update|anpassen)\b",
    r"\b(kaufen|purchase|abonnement|subscription)\b",
]


def classify(text: str) -> dict:
    t = text.lower()
    for p in RED_PATTERNS:
        if re.search(p, t):
            return {"gate": "RED", "reason": f"matches red pattern: {p}", "action": "STOP — require human decision"}
    for p in YELLOW_PATTERNS:
        if re.search(p, t):
            return {"gate": "YELLOW", "reason": f"matches yellow pattern: {p}", "action": "PREPARE — human approval required"}
    return {"gate": "GREEN", "reason": "no risk patterns matched", "action": "EXECUTE autonomously"}


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    print(json.dumps(classify(text), indent=2, ensure_ascii=False))
