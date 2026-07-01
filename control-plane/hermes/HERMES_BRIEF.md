# HERMES_BRIEF — Task-Eingabe für autonome Vorarbeit

## Goal
[Ein Satz: Was soll am Ende existieren?]

## Why now
[Business-Context, Deadline, Trigger]

## Constraints
- NICHT ändern: [...]
- NICHT senden: [...]
- NICHT kaufen: [...]
- Budget: [$X]
- Max. Zeit: [Xh]

## Success criteria
- [ ] Kriterium 1 (messbar)
- [ ] Kriterium 2 (messbar)
- [ ] Kriterium 3 (messbar)

## Risks
- [Risiko 1] → [Mitigation]
- [Risiko 2] → [Mitigation]

## Examples
- Gut: [Link/Datei/Beschreibung]
- Schlecht: [Was explizit vermieden werden soll]

## Output format
[Markdown / JSON / Code / E-Mail / etc.]

## Gate-Vermutung
- [ ] GREEN — Hermes kann autonom ausführen
- [ ] YELLOW — Hermes bereitet vor, Maurice entscheidet
- [ ] RED — Maurice muss vorher aktiv entscheiden

---

## First-Principles Note

Dieses Briefing dient einem System, das Bewegung von Verantwortung trennt.

Hermes wird autonom ausführen, was nur Arbeit ist.
Hermes wird Maurice an Entscheidungskanten liefern, wenn Verantwortung betroffen ist.

Jede Aufgabe, die hier definiert wird, sollte entweder eindeutig GREEN sein (reine Arbeit) oder eine klare YELLOW/RED-Kante haben.

Siehe `PHILOSOPHY.md` und `HERMES_RULES.md`.

---

## First-Principles Trigger

Dieses Briefing löst First-Principles-Mode aus, wenn:
- Das Thema strategisch, finanziell, rechtlich, technisch oder persönlich ist
- Mehrere konkurrierende Optionen existieren
- Die Aufgabe noch nie in dieser Form gelöst wurde
- Der Aufwand > 2 Stunden beträgt

Hermes verwendet dann automatisch `control-plane/hermes/HERMES_FIRST_PRINCIPLES_MODE.md` als Prozessrahmen.


## GRILL_ME Mode

Für komplexe Aufgaben (strategisch, finanziell, rechtlich, technisch, persönlich, Aufwand > 2h, YELLOW/RED-Gate) aktiviert Hermes automatisch `HERMES_GRILL_ME.md`.

Maximal 12 Fragen in 4 Phasen:
1. Ziel (3 Fragen)
2. Constraints (3 Fragen)
3. Kontext (3 Fragen)
4. Risiko + Optionen (3 Fragen)

Output: gegrilltes Briefing + First-Principles-Karte + Gate-Empfehlung + Decision Card (falls nötig).
