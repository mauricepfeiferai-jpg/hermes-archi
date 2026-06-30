#!/usr/bin/env python3
"""Learning Agent: extract rules from Decision Cards and update HERMES_RULES.md."""
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


def parse_decision_card(path: Path) -> dict:
    text = path.read_text()
    sections = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def infer_rule(card: dict) -> dict:
    """Infer a simple rule from a decision card."""
    goal = card.get("Ziel", "")
    decision_section = card.get("Entscheidung", "")

    # Determine selected option from checkboxes
    selected = None
    if "[x] GREEN" in decision_section:
        selected = "GREEN"
    elif "[x] YELLOW" in decision_section:
        selected = "YELLOW"
    elif "[x] RED" in decision_section:
        selected = "RED"

    # Extract rule heuristically
    rule = {
        "trigger": goal[:120],
        "gate": selected or "UNKNOWN",
        "rule": f"Bei '{goal[:60]}': {selected}-Gate anwenden. Risiken prüfen, Decision Card erstellen."
    }

    # Special simple heuristics for common cases
    if "post" in goal.lower() or "veröffentlich" in goal.lower() or "tweet" in goal.lower():
        rule["rule"] = "Jegliche öffentliche Veröffentlichung (Post/Tweet/Artikel) ist RED-Gate: Maurice muss vorher entscheiden."
        rule["gate"] = "RED"
    elif "e-mail" in goal.lower() or "email" in goal.lower() or "senden" in goal.lower():
        rule["rule"] = "Externe Kommunikation (E-Mail an Kunden/Partner) ist YELLOW-Gate: Entwurf vorbereiten, Maurice freigeben lassen."
        rule["gate"] = "YELLOW"
    elif "lösch" in goal.lower() or "delete" in goal.lower():
        rule["rule"] = "Löschaktionen auf Daten/Accounts/Production sind RED-Gate: nie autonom."
        rule["gate"] = "RED"

    return rule


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
        return

    text += entry + "\n"
    RULES_FILE.write_text(text)


def main():
    rules = load_learned_rules()
    initial_count = len(rules)
    processed = 0

    if not DECISIONS_DIR.exists():
        print("No decisions directory yet.")
        return

    for card_path in DECISIONS_DIR.glob("DC_*.md"):
        card_id = extract_decision_id(card_path)
        if any(r.get("source") == card_id for r in rules):
            continue  # already learned

        card = parse_decision_card(card_path)
        rule = infer_rule(card)
        rule["source"] = card_id
        rule["learned_at"] = now_iso()

        rules.append(rule)
        append_rule_to_rules_md(rule)
        processed += 1

    save_learned_rules(rules)

    emit("learning_agent.rules.updated", {
        "new_rules": processed,
        "total_rules": len(rules)
    })

    print(f"Learning Agent: processed {processed} new decision cards, total rules={len(rules)}")


if __name__ == "__main__":
    main()
