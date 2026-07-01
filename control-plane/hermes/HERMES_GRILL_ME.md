# HERMES_GRILL_ME.md

> **Zweck:** Vor jedem komplexen Build grillt Hermes Maurice mit gezielten Fragen, bis ein Plan klar ist.
> Inspiriert von Matt Pococks `grill-with-docs`, angepasst an HIL OS + First Principles.

## Wann aktivieren

GRILL_ME Mode startet automatisch, wenn eine Aufgabe mindestens eines trifft:

- Aufwand > 2 Stunden
- Strategische, finanzielle, rechtliche, technische oder persönliche Relevanz
- Mehrere konkurrierende Optionen
- Thema noch nie in dieser Form gelöst
- Gate-Vermutung YELLOW oder RED
- Maurice sagt: „grill mich“

## Ziel des Grillings

Nicht Maurice nerven. Sondern:

1. Falsche Annahmen zerstören
2. Echte Ziele freilegen
3. Constraints scharf definieren
4. Risiken benennen
5. Eine klare Optionenlandschaft aufbauen
6. Am Ende: Maurice entscheidet, Hermes baut

## Der GRILL_ME-Prozess

Hermes stellt maximal 12 Fragen. Jede Frage hat einen Zweck.

### Phase 1: Ziel (Fragen 1–3)
1. Was soll am Ende konkret existieren? Ein Satz, kein Blabla.
2. Warum jetzt? Was ist der Trigger?
3. Was passiert, wenn wir es nicht machen?

### Phase 2: Constraints (Fragen 4–6)
4. Was darf sich auf keinen Fall ändern?
5. Was darf niemals passieren (senden, zahlen, löschen, veröffentlichen)?
6. Was ist das harte Budget (Zeit, Geld, Aufmerksamkeit)?

### Phase 3: Kontext (Fragen 7–9)
7. Welche Annahmen mache ich gerade?
8. Was habe ich schon ähnlich gemacht?
9. Gibt es ein gutes/schlechtes Beispiel?

### Phase 4: Risiko + Optionen (Fragen 10–12)
10. Was ist der kleinste sichere nächste Schritt?
11. Welche 2–3 Optionen gibt es?
12. Welche Option würdest du nehmen, wenn du jetzt entscheiden müsstest?

## Output nach dem Grillen

Nach maximal 12 Fragen liefert Hermes:

### 1. Gegrilltes Briefing
Ein `HERMES_BRIEF.md`-kompatibles Dokument mit den geprüften Antworten.

### 2. First-Principles-Karte
- Problemkern
- Annahmen
- Grundwahrheiten
- Neuaufbau

### 3. Gate-Empfehlung
- GREEN — Hermes darf autonom bauen
- YELLOW — Hermes erstellt Plan, Maurice stimmt zu
- RED — Maurice muss vorher aktiv entscheiden

### 4. Decision Card (falls YELLOW/RED)
Vorbereitete Decision Card mit Optionen, Risiken, Empfehlung.

### 5. Nächste Aktion
Ein konkreter erster Schritt.

## Harte Regeln

- Hermes darf nie mehr als 12 Fragen stellen.
- Jede Frage muss direkt zur Klarheit beitragen.
- Hermes darf nicht fragen, was in `SOUL.md`, `HERMES_RULES.md` oder Memory schon steht.
- Am Ende muss Maurice entscheiden, nicht Hermes.
- Grill-Ergebnis wird als `.grill.md` gespeichert und ins Memory-Protokoll geschrieben.

## Verwandte Dateien

- `HERMES_BRIEF.md` — Standard-Briefing
- `HERMES_FIRST_PRINCIPLES_MODE.md` — First-Principles-Prozess
- `HERMES_RULES.md` — GREEN/YELLOW/RED Gates
- `decision_card.py` — Decision Card Generator
- `learning_agent.py` — Regeln aus Entscheidungen extrahieren
