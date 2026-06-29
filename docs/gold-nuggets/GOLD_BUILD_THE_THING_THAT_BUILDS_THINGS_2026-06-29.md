# 💰 Gold Nugget: Build The Thing That Builds Things

**Datum:** 2026-06-29  
**Status:** Roherkenntnis → Kernstrategie fuer AI Empire

## Die Erkenntnis

> Ich moechte das Ding bauen, welches die Dinge baut.

Statt einzelne Produkte zu bauen, baue ich die Fabrik, die Produkte baut.

## Was das bedeutet

- **Vorher:** Ein Gold Nugget = ein manuelles Produkt.
- **Jetzt:** Ein Gold Nugget = Input fuer die Product Factory.
- **Ziel:** Jede Idee wird automatisch zu PRODUCT.md + Landing Page + Pricing + HTML + Marketing.

## Warum das Kingmaker ist

- **Leverage:** Eine Fabrik produziert unendlich viele Produkte.
- **Speed:** Von Idee zu Live-Produkt in Minuten statt Stunden.
- **Trial & Error:** 100 Ideen testen statt 10.
- **Monetarisierung:** Jede gute Idee wird sofort verkaufsbereit.
- **Compounding:** Jede Produkt-Run verbessert die Fabrik (100x Loop).

## Konkrete Auspraegung: AI Empire Product Factory

**Input:** Gold Nugget (Problem, Loesung, Zahlen, Beweis)
**Output:** Vollstaendiges Produktpaket

```
Gold Nugget
    ↓
Product Factory Agent
    ↓
├── PRODUCT.md (claim, headline, pricing, CTA)
├── landing-page/LANDING_PAGE.md
├── sales-page/SALES_PAGE.md
├── pricing/PRICING.md
├── checkout/CHECKOUT.md
├── website/products/{slug}.html
├── go-to-market/14_DAY_LAUNCH_PLAN.md
├── go-to-market/COLD_OUTREACH_TEMPLATES.md
├── X-Thread-Entwurf
└── LinkedIn-Post-Entwurf
```

## Rollen in der Fabrik

| Agent | Rolle | Output |
|---|---|---|
| Product Strategist | Bewertet Idee nach Viral-Score | GO / NO-GO |
| Copywriter | Schreibt Headline, Subheadline, Problem, Loesung | Landing-Page-Copy |
| Pricing Agent | Setzt Popcorn-Preise | 3-Tier-Tabelle |
| Web Builder | Generiert HTML-Seite | website/products/{slug}.html |
| GTM Agent | Schreibt Launch-Plan + Cold-DMs | go-to-market/ |
| Retro Agent | Speichert Lessons in 100x Loop | Improvement Patch |

## Integration in AI Empire

- Input kommt aus `04_OUTPUT/GOLD_NUGGETS/`.
- Fabrik laeuft als Hermes Skill `ai-empire-product-factory`.
- Output landet in `hermes-archi/products/{slug}/`.
- Jeder Run endet mit Review + Retro.

## Naechste Schritte

1. `ai-empire-product-factory` Skill bauen.
2. Ersten automatischen Produkt-Run mit diesem Gold Nugget testen.
3. Fabrik mit 100x Loop verbinden.
4. Bestehende 6 Produkte als Trainingsbeispiele fuer die Fabrik nutzen.

## Verwandte Projekte

- One-Person AI Agent Company (`products/one-person-ai-agent-company/`)
- Self-Improvement 100x Loop (`~/.hermes/skills/orchestration/self-improvement-100x-loop`)
- Hermes Swarm Fan-Out (`~/.hermes/skills/orchestration/swarm-fan-out`)
- Gold Extract (`~/.agents/skills/gold-extract`)
