# Project Shippability Scoring — Started Codebases vs the 33 Viral Principles

Generated: 2026-06-29 · Author: Claude (Cowork) · Scope: **project-level** pass (real started codebases/products), distinct from the Codex agent's template/gold-nugget scoring.

Two axes:
- **Principles score (/33)** — the 32 viral principles + the 33rd ("ship the proof, not the promise"). Honest, not inflated.
- **Shippability (0–5)** — how close to actually charging money (paywall, landing, demo, one CTA, distribution).

Winner = best **finish-it-and-sell** bet = high on *both* axes, not just principle score.

Confidence: **HIGH** = product docs/code read directly; **MED** = structure/inventory only; **LOW** = name/inventory only.

---

## Inventory of real started projects (products & codebases, not notes/templates)

| Project | Location | What it is | State (runs? UI? payment? users?) | Conf. |
|---|---|---|---|---|
| **EvidenceHunter Pro** | `~/.openclaw/workspace/products/evidence-hunter-pro` | Forensic file discovery + evidence classification for macOS (legal) | Python pkg, `pip install`, CLI works, 4 tiers defined, SHA256 chain-of-custody, legal templates. No payment wiring / landing / GUI yet. Dogfooded on owner's real case. | HIGH |
| **Mac Optimizer** | `~/core` (repo `Maurice-AIEMPIRE/core`) | Premium Mac performance/cleanup software | Turbo/pnpm monorepo, apps/webapp + server + systemd, **Gumroad payment + Homebrew + curl install + CI/CD** wired, 30-day guarantee, pricing live (Free + $19). | HIGH |
| **skill-lab** | `/root/projects/skill-lab` | Productized AI skill packs + marketing/dist | `dist/`, `marketing/`, `skills/`, docs. Digital-product shaped; no storefront/pricing/CTA confirmed. | MED |
| **content-engine** | `/root/projects/content-engine` | Content/X growth engine + CRM + orchestrator | Real app: `crm/`, vite UI, `x_trend_engine`, `x_audience_loop`, loop_kernel, tests. Internal-tool shaped; no payment/landing seen. | MED |
| **kmu-intelligence-os** | `/root/projects/kmu-intelligence-os` | SMB ("KMU") intelligence OS | `clients/`, `pilots/`, `playbooks/`, `templates/`. Productized **service**, not self-serve product. Pilots suggest near-term service revenue. | MED |
| **GBrain** | `~/gbrain-latest` | Local-first AI memory engine / OpenClaw plugin (dev tool) | Bun/TS, `src/`, evals, `llms.txt`, `openclaw.plugin.json`, recipes. Pre-revenue; no pricing/landing. | HIGH |
| **Archi (Hermes-Archi)** | `~/ai-empire/projects/hermes-archi` | The agent platform itself (brand umbrella) | Control-plane, model-layer, telegram, integrations, website/, products/. A *platform*, not a single packaged SKU. | HIGH |
| **loop-master** | `/root/projects/loop-master` | Agent governance / decision-cards / dashboard | Infra/governance; internal. | MED |
| **content/trading** (ai-alpha-miner, karpathy-trading-loop) | `/root/projects/*` | Trading research/strategies | Research-grade; **not sellable** (regulated, risky claims). | MED |
| **v0.1 scaffolds** (loopos_v0_1, hecate_agent_company_v0_1) | `~/ai-empire/projects/*` | Early agent-company/loop scaffolds | Pre-product. | LOW |

---

## Scoring

| Project | Principles /33 | Ship 0–5 | Headline read |
|---|---|---|---|
| **EvidenceHunter Pro** | **22** | **3.5** | Best principle-fit; proof-native (#33 = SHA256 chain of custody); premium 4-tier pricing; real differentiated pain. Needs payment + landing. |
| **Mac Optimizer** | 17 | **4.0** | Closest to first dollar (payment + distribution already wired). But commodity market, thin moat, free-tier + $19 = low ceiling. |
| **skill-lab** | 14 | 3.0 | Fastest *digital-product* cashflow if given a storefront; ship-in-public fit. |
| **content-engine** | 13 | 2.5 | Powerful, but internal-tool shaped; long road to self-serve. |
| **kmu-intelligence-os** | 13 | 2.5 | Can bill *pilots* as a service now; not a viral self-serve product. |
| **GBrain** | 12 | 2.0 | Strong dev-tool/infra; pre-revenue, dev audience, not consumer-viral. |
| **Archi (platform)** | 16 | 1.5 | High concept (see positioning work), but a sprawl — no single packaged SKU to charge for *yet*. It's the umbrella; the SKUs below are how it earns. |
| loop-master | 9 | 1.0 | Internal infra. |
| trading (alpha-miner / karpathy) | 6 | 0.5 | Not sellable (regulatory/claims risk). |
| v0.1 scaffolds | 7 | 1.0 | Pre-product. |

---

## Ranked shippability shortlist (finish-and-sell bets)

1. **EvidenceHunter Pro** — 22/33 · 3.5/5 — **#1 bet.** Highest principle-fit *and* near-shippable, premium price points, and a moat almost nobody can copy: the proof is *in the product* (SHA256 chain-of-custody = Principle 33 made literal). Differentiated pain, dogfooded on a real case (founder-in-the-open, #23).
2. **Mac Optimizer** — 17/33 · 4.0/5 — **fastest first dollar / quick-cash + ship-in-public proof.** Payment + distribution already wired; the gap is positioning, not plumbing. Lower ceiling (commodity "Mac cleaner" space; verify performance claims to avoid #5/#33 over-promise).
3. **skill-lab** — 14/33 · 3.0/5 — **cheapest path to a live storefront**; package the skill packs as good/better/best on Gumroad, ship in public.

Everything else: keep as engine/infra (GBrain, content-engine, Archi platform), service (kmu-os pilots), or park (trading, scaffolds).

---

## Finish-to-production-and-ship plans (Top 3)

### #1 — EvidenceHunter Pro

**v1 cut (ship this, cut the rest):** CLI + A/B/C/R classification + SHA256 manifest + XLSX/CSV court-ready report + ChatGPT-export parser. Defer multi-case, DSGVO/Kammertermin generators, Enterprise API to v1.1.

**What's left to build:**
- Payment + license: Gumroad (reuse Mac Optimizer's Gumroad/license-server pattern from `~/core/scripts/deploy/to-gumroad.sh`) — biggest gap.
- One landing page (hero sells alone, #6): headline + 30-sec demo GIF of a scan producing a verified manifest + one CTA. Reuse `hermes-archi/website/`.
- Light GUI or a guided `--wizard` so time-to-value < 60s (#24) for non-CLI buyers.
- Legal-disclaimer / synthetic-demo gate (sensitive domain).

**Pricing (popcorn — already strong, keep):** Basic €99 → **Pro €297 (anchor/star)** → Legal Pro €797 → Enterprise €4,997/yr. Anchor by showing Legal Pro first (#17).

**One CTA:** "Scan your case — get a court-ready, hashed archive in minutes." (same button everywhere)

**Where to sell:** Gumroad (instant), then direct to German legal/HR/SME audiences (LinkedIn, Anwalts/Fachforen, the owner's own legal saga as the case study). Founder-in-open story = distribution.

**Principles currently violated -> fix:**
- #6/#7 (hero + one CTA): no landing yet -> ship the one-page hero.
- #9 (show the product): CLI-only -> add a demo GIF/screenshot of the verified manifest.
- #24 (TTV < 60s): CLI friction -> `--wizard` / GUI quick scan.
- #14 (hard paywall): license not enforced -> wire Gumroad license check.

**TrustMRR tie-in:** this product *is* the TrustMRR thesis incarnate — recurring revenue follows verifiable, receipt-bearing output. (Note: specific TrustMRR figures were not available in-session; drop them in and they fold straight into the landing's proof block.)

### #2 — Mac Optimizer (quick-cash + proof-in-public)

**v1 cut:** the 9-fix optimizer + scheduler + notifications. Already essentially built.

**What's left:** real landing page (not just PRODUCT.md); **remove the free tier -> 7-day trial** (#13); add a before/after **proof readout** (reclaimed RAM/disk, ms saved) so it obeys #33 instead of making unverifiable speed claims; restructure pricing.

**Pricing (fix the violations):** drop single $19 -> **Lite $19 / Pro $39 / Lifetime $79** (popcorn #15, anchor #17, charge-more #16). Annual or lifetime, no permanent free tier.

**One CTA:** "Speed up your Mac now — see the proof." Sell on Gumroad + Homebrew (both wired).

**Principles violated -> fix:** #13 free-kills (-> trial), #15 popcorn (-> 3 tiers), #16 charge-more (-> raise), #33 proof (-> show measured before/after), #5 bold-but-true (verify claims to stay honest).

### #3 — skill-lab (fastest storefront)

**v1 cut:** bundle the top 3–5 skills as one "pack." **What's left:** Gumroad listing + 3-tier pack pricing + one demo. **Pricing:** Single pack €29 / Bundle €79 / All-access €199. **CTA:** "Install the pack, ship today." **Violations -> fix:** #2 one-promise (name the outcome), #9 show-the-product (demo), #14 paywall (Gumroad).

---

## Reconciliation with the Codex agent's scoring

Codex scored **knowledge/templates ("gold nuggets")**: One-Person AI Agent Company Template 18/32, Hermes Swarm Fan-Out 15/32, AI Stack Chinese Models Playbook 13/32. My pass scores **actual started codebases/products** — a different object, so this is complementary, not contradictory.

- **Agree:** "One-Person AI Agent Company" (Codex 18/32) is the *strategy* behind Archi and these SKUs — it's the highest-value *playbook*. My equivalent at the platform level (Archi 16/33) is close; the gap is that a playbook isn't a chargeable SKU.
- **Differ (intentionally):** I rank **EvidenceHunter Pro and Mac Optimizer above all three Codex nuggets** for *shipping*, because they have code + pricing + (Mac Optimizer) live payment/distribution. Codex's objects are guides; mine are products. A guide scores well on principles but earns $0 until it's productized.
- **New axis:** the 33rd principle ("ship the proof") and the shippability 0–5 axis aren't in Codex's /32 — and they're exactly what separates "viral on paper" from "charging money." EvidenceHunter wins largely *because* of the 33rd.
- **Net:** use Codex's nuggets as the *marketing/positioning library*; use this list as the *build-and-bill queue*. Finish EvidenceHunter Pro first.

---

_Additive analysis. Does not modify other files. Vault-merge and OpenCLAW exec decisions remain pending and untouched._
