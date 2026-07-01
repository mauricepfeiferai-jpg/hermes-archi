# Demonstration: Daily Mail Triage

- captured_at: 2026-07-01T15:33:17
- skill_name: daily_mail_triage
- trigger_phrases: Daily Mail Triage, mache Mail Triage, sortiere meine Mails, was ist wichtig im Posteingang
- agent: executive_assistant
- red_gates: send_email, delete_file, mark_as_read, move_to_trash

## Goal
Lese ungelesene Apple Mail, filtere Noise heraus, identifiziere wichtige/absender-basierte Mails und speichere eine kurze Zusammenfassung in CURRENT.md.

## Steps
1. Lade die 20 neuesten ungelesenen Mails.
2. Ignoriere Newsletter, Promotions, automatische Status-Mails.
3. Markiere Mails von bekannten Kunden, mit Fristen, Rechnungen oder Angeboten als wichtig.
4. Fasse die wichtigen Betreffzeilen und Absender zusammen.
5. Speichere die Zusammenfassung in CURRENT.md unter "Mail Triage".

## Example Invocation
- User: "Mache Daily Mail Triage"
- User: "Was ist wichtig im Posteingang?"

## Data Sources
- Apple Mail (via SQLite/JXA connector)
- ~/.openclaw/workspace/ai-empire/memory/CURRENT.md

## Notes
This skill was demonstrated by Maurice. Red Gates: never send, delete, move or mark-as-read mail without explicit approval.
