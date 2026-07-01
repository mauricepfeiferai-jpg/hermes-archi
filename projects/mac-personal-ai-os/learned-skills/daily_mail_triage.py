#!/usr/bin/env python3
"""Learned skill: Daily Mail Triage."""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

HOME = Path.home()
MQC = HOME / "ai-empire" / "projects" / "hermes-archi" / "projects" / "mac-personal-ai-os"
sys.path.insert(0, str(MQC / 'core'))
import mqc_skill_runner

SKILL_NAME = 'daily_mail_triage'
TRIGGER_PHRASES = ['Daily Mail Triage', 'mache Mail Triage', 'sortiere meine Mails', 'was ist wichtig im Posteingang']
AGENT = 'executive_assistant'
RED_GATES = ['send_email', 'delete_file', 'mark_as_read', 'move_to_trash']

# Noise patterns Maurice wants to ignore
NOISE_SENDERS = [
    "no-reply", "noreply", "newsletter", "mailing", "promotion", "promotions",
    "amazon.de", "netto", "onefootball", "samsung", "adac", "dirkkreuter",
    "clinicasaneva", "saturn", "ebay", "otto", "zalando", "bonprix", "shein",
]
NOISE_SUBJECTS = [
    "rabatt", "angebot", "sale", "aktion", "gutschein", "%," "topseller",
    "wm-updates", "news", "täglich", "daily", "deal", "sparen", "bestellen",
]
# High-signal keywords
IMPORTANT_SUBJECTS = [
    "rechnung", "invoice", "zahlung", "frist", "termin", "angebot", "angebotsanfrage",
    "klage", "beweis", "richter", "anwalt", "kunde", "auftrag", "bestellung",
    "paypal", "buchhaltung", "steuer", "versicherung", "mahnung",
]
IMPORTANT_SENDERS = [
    "steuer", "finanzamt", "versicherung", "anwalt", "kanzlei", "gericht",
    "kunde", "auftraggeber", "bauamt", "vds", "dak", "aok", "tk", "barmer",
]


def is_noise(mail: dict) -> bool:
    sender = (mail.get("sender") or "").lower()
    subject = (mail.get("subject") or "").lower()
    return any(n in sender for n in NOISE_SENDERS) or any(n in subject for n in NOISE_SUBJECTS)


def is_important(mail: dict) -> bool:
    sender = (mail.get("sender") or "").lower()
    subject = (mail.get("subject") or "").lower()
    return any(k in subject for k in IMPORTANT_SUBJECTS) or any(k in sender for k in IMPORTANT_SENDERS)


def summarize_mails(mails: list) -> str:
    total = len(mails)
    noise = [m for m in mails if is_noise(m)]
    important = [m for m in mails if is_important(m)]
    rest = [m for m in mails if m not in noise and m not in important]
    lines = [
        f"Mail Triage ({datetime.now().strftime('%Y-%m-%d %H:%M')}): {total} ungelesene Mails",
        f"- Davon als Noise/Promo eingestuft: {len(noise)}",
        f"- Davon als wichtig eingestuft: {len(important)}",
    ]
    if important:
        lines.append("Wichtige Mails:")
        for m in important[:5]:
            lines.append(f"  - [{m.get('date', '?')[:10]}] {m.get('sender', '?')}: {m.get('subject', '?')}")
    if rest:
        lines.append("Weitere Mails zum Prüfen:")
        for m in rest[:5]:
            lines.append(f"  - [{m.get('date', '?')[:10]}] {m.get('sender', '?')}: {m.get('subject', '?')}")
    if not important and not rest:
        lines.append("Nur Promotions/Newsletter im Posteingang.")
    return "\n".join(lines)


def append_to_current(summary: str) -> dict:
    current = HOME / ".openclaw" / "workspace" / "ai-empire" / "memory" / "CURRENT.md"
    try:
        existing = current.read_text(encoding="utf-8") if current.exists() else ""
        entry = f"\n\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} — Mail Triage\n\n{summary}\n"
        current.write_text(existing.rstrip() + entry, encoding="utf-8")
        return {"success": True, "path": str(current)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run(payload: dict = None) -> dict:
    payload = payload or {}
    results = []

    # Step 1: load unread mail directly (runner truncates stdout)
    limit = payload.get("limit", 20)
    from connectors.mail_connector import read_mail
    mail_data = read_mail(limit=limit)
    results.append({"step": "Lade ungelesene Mails", "count": mail_data.get("count")})

    mails = mail_data.get("messages", [])

    # Step 2: classify
    noise = [m for m in mails if is_noise(m)]
    important = [m for m in mails if is_important(m)]
    results.append({"step": "Klassifiziere Mails", "total": len(mails), "noise": len(noise), "important": len(important)})

    # Step 3: summarize
    summary = summarize_mails(mails)
    results.append({"step": "Zusammenfassung", "summary": summary})

    # Step 4: save to CURRENT.md
    save_result = append_to_current(summary)
    results.append({"step": "Speichere in CURRENT.md", "save_result": save_result})

    return {"success": True, "skill": SKILL_NAME, "agent": AGENT, "summary": summary, "results": results}


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--payload", default="{}")
    args = p.parse_args()
    payload = json.loads(args.payload)
    print(json.dumps(run(payload), ensure_ascii=False, indent=2))
