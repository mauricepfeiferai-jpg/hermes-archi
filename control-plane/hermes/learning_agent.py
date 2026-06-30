#!/usr/bin/env python3
"""Learning Agent: extract rules from Decision Cards and First-Principles analyses, update HERMES_RULES.md."""
import json, re
from pathlib import Path
from datetime import datetime, timezone

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"
RULES_FILE = REPO / "control-plane" / "hermes" / "HERMES_RULES.md"
DECISIONS_DIR = REPO / "control-plane" / "decisions"
LESSONS_FILE = REPO / "state" / "hil" / "learned_rules.json"
BUS_DIR = REPO / "state" / "neural-bus"


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def emit(event_type: str, payload: dict):
    BUS_DIR.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": now_iso(),
        "type": event_type,
        "source": "learning_agent.py",
        "payload": payload,
        "recipients": ["emperor"]
    }
    ts = now_iso().replace(":", "-").replace(".", "-")
    (BUS_DIR / f"{ts}_{event_type}.json").write_text(json.dumps(event, indent=2))


def extract_decision_id(path: Path) -> str:
    m = re.search(r"DC_(\d{8})_([a-f0-9]+)", path.name)
    return m.group(0) if m else path.name


def parse_sections(text: str) -> dict:
    """Parse markdown sections into dict."""
    sections = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## ") or line.startswith("### "):
            current = line.strip("# ").strip()
            sections[current] = []
        elif current:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def extract_learning_rule(text: str) -> str | None:
    """Extract Learning Rule from First-Principles analyses."""
    # Look for section 7. Learning Rule or similar
    sections = parse_sections(text)
    for key in sections:
        if "learning rule" in key.lower() or "gelernte regel" in key.lower() or "learned" in key.lower():
            content = sections[key]
            # Find blockquote or first bullet
            for line in content.splitlines():
                line = line.strip()
                if line.startswith(">"):
                    return line.strip("> ").strip()
                if line.startswith("-") or line.startswith("*"):
                    return line.strip("- *").strip()
            # Return first non-empty line
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    return line
    return None


def extract_gate_from_decision_card(text: str) -> str:
    """Extract selected option from Decision Card checkboxes."""
    # Look for checked option
    if re.search(r"\[x\]\s*Option\s*A", text, re.I):
        return "YELLOW"  # strategy decisions are typically YELLOW
    if re.search(r"\[x\]\s*Option\s*B", text, re.I):
        return "YELLOW"
    if re.search(r"\[x\]\s*Option\s*C", text, re.I):
        return "YELLOW"
    if re.search(r"\[x\]\s*GREEN", text, re.I):
        return "GREEN"
    if re.search(r"\[x\]\s*YELLOW", text, re.I):
        return "YELLOW"
    if re.search(r"\[x\]\s*RED", text, re.I):
        return "RED"
    return "YELLOW"


def infer_rule(path: Path, text: str) -> dict:
    """Infer a rule from a decision card or FP analysis."""
    card_id = extract_decision_id(path)

    # Try to extract learning rule from First-Principles analyses
    learning_rule = extract_learning_rule(text)
    if learning_rule:
        return {
            "source": card_id,
            "gate": "YELLOW",
            "trigger": "First-Principles Entscheidung",
            "rule": learning_rule,
            "learned_at": now_iso()
        }

    # Fallback: parse Decision Card sections
    sections = parse_sections(text)
    goal = sections.get("Ziel", sections.get("Goal", path.name))
    recommendation = sections.get("Empfehlung", "")
    gate = extract_gate_from_decision_card(text)

    # Heuristic rule construction
    rule_text = f"Bei '{goal[:80]}': {gate}-Gate anwenden. Risiken prüfen, Decision Card erstellen."

    if recommendation:
        rule_text = recommendation[:180] + " (" + gate + "-Gate)"

    # Special simple heuristics for common cases
    t = text.lower()
    if any(w in t for w in ["post", "veröffentlich", "publish", "tweet"]):
        rule_text = "Jegliche öffentliche Veröffentlichung (Post/Tweet/Artikel) ist RED-Gate: Maurice muss vorher entscheiden."
        gate = "RED"
    elif any(w in t for w in ["e-mail", "email", "senden", "send"]):
        rule_text = "Externe Kommunikation (E-Mail an Kunden/Partner) ist YELLOW-Gate: Entwurf vorbereiten, Maurice freigeben lassen."
        gate = "YELLOW"
    elif any(w in t for w in ["lösch", "delet"]):
        rule_text = "Löschaktionen auf Daten/Accounts/Production sind RED-Gate: nie autonom."
        gate = "RED"
    elif "monetarisier" in t or "10k" in t or "$" in t:
        rule_text = "Bei Monetarisierungsfragen priorisiere den Pfad, der Maurice' echte Domain-Expertise und höchsten Kundenschmerz nutzt, bevor generische digitale Produkte ohne Publikum bevorzugt werden."
        gate = "YELLOW"

    return {
        "source": card_id,
        "gate": gate,
        "trigger": goal[:120],
        "rule": rule_text,
        "learned_at": now_iso()
    }


def load_learned_rules() -> list:
    LESSONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if LESSONS_FILE.exists():
        try:
            return json.loads(LESSONS_FILE.read_text())
        except Exception:
            return []
    return []


def save_learned_rules(rules: list):
    LESSONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    LESSONS_FILE.write_text(json.dumps(rules, indent=2, ensure_ascii=False))


def append_rule_to_rules_md(rule: dict):
    """Append a learned rule to the dynamic learned rules section of HERMES_RULES.md."""
    if not RULES_FILE.exists():
        return
    text = RULES_FILE.read_text()
    marker = "## Dynamisch gelernte Regeln (Learning Agent)"
    entry = f"\n- **{rule['gate']}** — {rule['rule']} *(gelernt aus {rule.get('source', 'unbekannt')})*"

    if marker not in text:
        text += f"\n\n---\n\n{marker}\n\nDieser Abschnitt wird automatisch vom Learning Agent aus Decision Cards ergänzt.\n"

    # Avoid duplicate rules
    if entry.strip() in text:
        return False

    text += entry + "\n"
    RULES_FILE.write_text(text)
    return True


def main():
    rules = load_learned_rules()
    initial_count = len(rules)
    processed = 0
    appended = 0

    if not DECISIONS_DIR.exists():
        print("No decisions directory yet.")
        return

    for card_path in DECISIONS_DIR.glob("*.md"):
        card_id = extract_decision_id(card_path)
        if any(r.get("source") == card_id for r in rules):
            continue  # already learned

        text = card_path.read_text()
        rule = infer_rule(card_path, text)

        rules.append(rule)
        if append_rule_to_rules_md(rule):
            appended += 1
        processed += 1

    save_learned_rules(rules)

    emit("learning_agent.rules.updated", {
        "new_rules": processed,
        "total_rules": len(rules),
        "appended_to_rules_md": appended
    })

    print(f"Learning Agent: processed {processed} new decision cards, appended {appended} rules, total={len(rules)}")


if __name__ == "__main__":
    main()
