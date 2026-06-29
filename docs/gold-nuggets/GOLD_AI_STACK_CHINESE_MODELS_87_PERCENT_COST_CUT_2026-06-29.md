# 💰 Gold Nugget: AI-Stack Migration to Chinese Models — 87% Cost Cut

**Datum:** 2026-06-29  
**Quelle:** Maurice Insight — eigenes AI-Stack-Replatforming  
**Status:** Roherkenntnis / Migration Playbook in Arbeit

## Die Erkenntnis

> Mein kompletter AI-Stack ist jetzt chinesisch. 87% günstiger. Gleicher Umsatz.

30-Tage-Resultat:
- Operating costs: -87%
- Output quality: -4% im Durchschnitt
- Revenue: unverändert
- Zusatznutzen: lokal lauffähig, Datenschutz, lernfähig, Ban-Risiko geringer

## Task-to-Model Routing

| Task | Vorher | Nachher | Benchmark Gap | Preisvorteil |
|---|---|---|---|---|
| Reasoning / Backend Brain | Opus 4.8 | Kimi K2.7 | ~8% | ~11x billiger |
| Code Generation | GPT-5.5 | Qwen 3.7 Max | ~18% | ~7x billiger |
| Agent Loops + Tool Calling | Sonnet 4.7 | GLM 5.2 | ~3% | ~5x billiger (Input) |
| Cheap Volume / Bulk Processing | GPT-5.5 mini | MiMo V2.5 | ~6% | ~12x billiger |
| Image Generation | GPT-Image-2 | Wan 2.5 | ~5% | ~8x billiger |
| Video Generation | Sora 2 | Kling 3.0 | ~gleich | ~6x billiger |

## Strategische Werte

1. **Kostenkontrolle:** 87% weniger OpEx bei gleichem Revenue → Margin explodiert.
2. **Souveränität:** Keine Abhängigkeit von US-Modellen; Ban-Risiko und API-Zugriffsrisiko sinken.
3. **Datenschutz:** Daten bleiben lokal oder in kontrollierter Umgebung.
4. **Lernfähigkeit:** Modelle können lokal gefinetuned/angelernt werden.
5. **Wettbewerbsvorteil:** Weniger Kosten = mehr Spielraum für Preise, Investitionen, Skalierung.

## Wo Western-Modelle noch bleiben

- 2 Fälle (laut Maurice) — noch zu spezifizieren.
- Vermutung: hochsensible Vertrags-/Rechtsarbeit und Kundenkommunikation mit hoher Haftung.

## Monetarisierungswinkel

1. **Migration-as-a-Service:** Anderen Unternehmen/Technikern den Stack migrieren.
2. **Kurs/Playbook:** "Weekend Migration Playbook" als digitales Produkt.
3. **Agent-Factory mit chinesischem Stack:** Günstigere Agent-Teams = höhere Margen.
4. **BMA-Dienstleister-Beratung:** Lokale, günstige, souveräne AI für Angebotserstellung, Dokumentation, Kundenkommunikation.
5. **Content-Reihe:** Tagesberichte, Benchmarks, Routing-Logik, Sicherheitsaspekte.

## Risiken & Gegenmassnahmen

| Risiko | Gegenmassnahme |
|---|---|
| Qualitätsverlust bei Code (-18%) | Qwen 3.7 Max für Code reviewen; ggf. Western-Modell als Checker für kritische Code-Reviews |
| API-Stabilität chinesischer Anbieter | Fallback-Layer, lokale Modelle, Multi-Provider-Setup |
| Datenschutz-/Compliance-Bedenken | Lokal runnable; keine sensitive Daten in Shared Cloud |
| Zukünftige Sanktionen/Bans | Lokal runnable macht unabhängig; europäische Fallback-Optionen prüfen |

## Nächste Schritte

1. Detaillierten Routing-Layer in Hermes/OpenClaw umsetzen (task → model → provider).
2. Benchmark-Harness für 6 Task-Kategorien bauen (Korrektheit, Latenz, Kosten).
3. Western-Modelle-Reserve-Policy definieren: wann welches Modell als Fallback.
4. Lokal-runnable-Plan: Welche Modelle auf Mac/Hetzner, welche nur Cloud.
5. Migration Playbook als Produkt aufbereiten.

## Verwandte Projekte

- Hermes Agent System (`~/.hermes/`)
- Karpathy Agent OS / Masterclass (`09_LIBRARY/github/andrej-karpathy-skills`)
- Mac Performance Steward (`~/.local/bin/mac-steward.sh`)
- AI Brain Navigator (`04_OUTPUT/GOLD_NUGGETS/GOLD_SECOND_BRAIN_NAVIGATION_GRAPH_QWYTHOS_2026-06-29.md`)

## Weitere Inputs

- Vollständiger Artikel folgt: Routing-Logik, 2 Western-Ausnahmen, Weekend Migration Playbook.
