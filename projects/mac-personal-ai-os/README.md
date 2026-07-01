# Mac Personal AI Operating System (MQC)

Maurice' Mac als zentraler Orchestrations- und Datenhub für Hermes + OpenClaw.

## Kurzbeschreibung

Dieses Projekt macht deinen Mac zum „Personal AI Operating System“:
- **Alle Daten lesbar**: ein lokaler Index über ai-empire, Hermes, OpenClaw, Codex, Obsidian, System
- **Hermes + OpenClaw verbunden**: Bridge routet Befehle vom Chat/Mobile an die richtigen Agenten
- **Persönliche Assistenten**: Registry mit Rollen (Executive, Research, Engineering, Business, Legal, BMA)
- **Lernen durch Vormachen**: Demonstrationen werden in Skills verwandelt

## Schnellstart

```bash
cd ~/ai-empire/projects/mac-personal-ai-os
./mqc.sh index      # Mac-Daten indexieren
./mqc.sh query --find "CURRENT.md"
./mqc.sh bridge "Mache meine Morgenroutine"
./mqc.sh learn      # Demonstration aufzeichnen
```

## Struktur

```
mac-personal-ai-os/
├── mqc.sh                         # Entry Point
├── README.md                      # Diese Datei
├── core/
│   ├── mac_data_indexer.py        # Indiziert lokale Daten
│   ├── mac_query.py               # Abfrage über den Index
│   ├── hermes_openclaw_bridge.py  # Routet Intents an Hermes
│   ├── mqc_skill_runner.py        # Lokale Skill-Ausführung
│   ├── assistant_registry.yaml    # Rollen-Definitionen
│   └── demonstration_capture_template.md
├── learned-skills/                # Aus Demonstrationen gelernte Skills
│   ├── memory_update_session_end.py
│   ├── run_executive_morning_routine.py
│   └── DEMO_*.md
├── assistants/                    # Zukünftige Agent-Implementationen
├── data-connectors/               # Zukünftige App-Connectors
└── docs/
    └── MAC_PERSONAL_AI_OS.md      # Architektur-Dokument
```

## Index

- Speicherort: `~/.mqc/index.jsonl` und `~/.mqc/mac_data.db`
- Enthält: ai-empire, Hermes, OpenClaw, Codex, Obsidian, Crontab, Disk, Prozesse

## Assistenten

| Assistent | Rolle | Datenquellen |
|---|---|---|
| executive_assistant | Tagesplanung, Memory | Memory, Gold Nuggets |
| research_assistant | Recherche, Knowledge Cards | Library, Documents, Wiki |
| engineering_assistant | Coding, Deployments | ai-empire projects, Hermes skills |
| business_assistant | Verkauf, Produkte | products, outputs |
| legal_assistant | Fristen, Beweise | LEGAL_SCAN_PRODUCT, Recht-Docs |
| bma_assistant | Brandmeldeanlagen | BMA-Templates, BMA-Docs |

## Lernen durch Vormachen

1. Führe einen Task manuell aus.
2. Fülle `core/demonstration_capture_template.md` aus.
3. Hermes generiert daraus einen Skill in `learned-skills/`.
4. Assistant Registry merkt, dass dieser Assistent den Skill kann.
5. Nächstes Mal: Assistent führt den Skill aus.

## Sicherheit

- Alle Daten indexiert lokal.
- RED Gates für: Senden, Zahlen, Löschen, Recht, Veröffentlichen.
- Kein automatischer Cloud-Fallback.

## Status

2026-07-01: MVP lauffähig. Indexer, Query, Bridge, Skill Runner, Assistant Registry und erste gelernte Skills vorhanden.

## Nächste Schritte

1. OpenClaw Telegram-Channel vollständig aktivieren
2. Erste reale Demonstration aufzeichnen und skillifizieren
3. App-spezifische Connectors (Mail, Calendar, Messages)
4. MQC in Hermes Silver Loops integrieren
