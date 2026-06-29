# AI Empire Product Factory

## Mission

**Turn every Gold Nugget into a shippable product in minutes.**

## How It Works

1. Drop a Gold Nugget into `inputs/`.
2. Run the factory: `python3 scripts/build_product.py --input inputs/GOLD_*.md`.
3. Get a complete product package in `outputs/{slug}/`.

## Factory Agents

| Agent | File | Role |
|---|---|---|
| Strategist | `agents/strategist.md` | Scores idea, decides GO/NO-GO |
| Copywriter | `agents/copywriter.md` | Writes landing page copy |
| Pricing Agent | `agents/pricing.md` | Sets 3-tier popcorn pricing |
| Web Builder | `agents/web_builder.md` | Generates HTML page |
| GTM Agent | `agents/gtm.md` | Writes launch plan + outreach |
| Retro Agent | `agents/retro.md` | Logs lessons to 100x loop |

## Templates

- `templates/PRODUCT.md`
- `templates/LANDING_PAGE.md`
- `templates/SALES_PAGE.md`
- `templates/PRICING.md`
- `templates/CHECKOUT.md`
- `templates/14_DAY_LAUNCH_PLAN.md`
- `templates/COLD_OUTREACH_TEMPLATES.md`

## Status

PROTOTYPE — first automated run pending.
