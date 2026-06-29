# Production Runbook: AI Empire Top Products

**Created:** 2026-06-29 21:22  
**Status:** READY FOR PRODUCTION  
**Top Product:** One-Person AI Agent Company Template

---

## Executive Decision

Go live with the best product first, then scale to others.

**Selected launch order:**

1. One-Person AI Agent Company Template — $149 Professional
2. Hermes Swarm Fan-Out Skill — $79
3. Self-Improvement 100x Loop — $69
4. Chinese AI Stack Migration Playbook — $129
5. Git Workflow for AI Workspaces — $59
6. Karpathy Agent OS Starter Kit — $199 (early access)

---

## Phase 1: Top Product Production (Next 60 Minutes)

### 1.1 Hosting

**Problem:** GitHub Pages blocked (private repo on free plan).
**Solution:** Netlify Drop.

```bash
# Already prepared:
# /tmp/ai-empire-products-drop.zip
# Open: https://app.netlify.com/drop
# Drag zip to drop zone
# Copy live URL
```

### 1.2 Payment

**Platform:** Gumroad (existing account: mauricepfeifer6.gumroad.com)

Create product:
- Name: One-Person AI Agent Company Template
- Price: €149 (Professional) / €49 (Starter) / €499 (Founder)
- Content: Zip with templates from `products/one-person-ai-agent-company/templates/`
- URL slug: `one-person-ai-agent-company`

### 1.3 Update Buy Links

Edit these files with real Gumroad URL:
- `website/products/one-person-ai-agent-company.html`
- `docs/ai-empire-products/one-person-ai-agent-company.html`
- `products/one-person-ai-agent-company/checkout/CHECKOUT.md`

Replace:
```
https://mauricepfeifer6.gumroad.com/l/one-person-ai-agent-company
```

### 1.4 Launch Content

**X/Twitter Thread:**
```
I built a company with 7 AI agents and 0 employees.

Here's the exact folder structure + cron jobs I use:

[screenshot of ai-company/ folder]

→ CEO
→ CTO
→ Engineer
→ Researcher
→ Writer
→ Sales
→ Ops
→ Loop (review/retro/self-improve)

Every role is a folder. Every job is a markdown file. No payroll.

I packaged it. $149 one-time.

[link]
```

**LinkedIn Post:**
```
37 years old. 16 years as electrical master. Running a one-person AI company.

7 agents. 10 cron jobs. 0 employees.

I turned my setup into a template for solo founders who want to scale without hiring.

If you're drowning in operational work before you can grow, this is for you.

Link in comments.
```

**Cold DM Template:**
```
Hi [Name], I saw you [specific observation]. 

Most solo founders hit the same wall: they want to scale but hiring kills margins.

I built a system that runs a company with 7 AI agents and 10 cron jobs — no employees, no payroll.

Worth a look? [link]
```

---

## Phase 2: Monitoring + 100x Loop

### 2.1 5 Tmux Windows Setup

| Window | Role | Agent | First Principle |
|---|---|---|---|
| 1 | Hermes Gateway Health | Hermes Monitor | Gateway up = empire runs |
| 2 | OpenClaw Tools | OpenClaw Monitor | Tools must be discoverable |
| 3 | Claude/Codex Skills | Skill Monitor | Right skill for right task |
| 4 | Product Factory / Git | Shipping Monitor | Every idea ships |
| 5 | 100x Loop Aggregator | Retro Agent | Every failure becomes a rule |

### 2.2 100x First-Principles Questions

Ask every 60 minutes:
1. What is the single point of failure right now?
2. Which product has the highest revenue potential per hour invested?
3. What is the smallest change that could 10x output?
4. What should we stop doing?
5. What rule, if added, would prevent the last problem?

---

## Phase 3: Scale (After First Sale)

1. Replicate launch playbook for product #2 (Swarm Fan-Out).
2. Build AI Agent Cost Calculator lead magnet.
3. Product Hunt launch for One-Person AI Agent Company.
4. pSEO pages for niche use-cases.
5. Newsletter sponsorships.

---

## Success Metrics

| Metric | Target | Deadline |
|---|---|---|
| First sale | 1 | Today |
| Landing page visits | 100 | 7 days |
| Email signups | 50 | 7 days |
| Revenue | €500 | 30 days |
| Products live | 6 | 14 days |

---

## Risk Controls

- No runtime changes during launch.
- No new dependencies without isolated test.
- No secrets in GitHub.
- Every change committed with clear message.
- Daily retro at 20:00.

---

## Next Action

**APPROVE GO LIVE: One-Person AI Agent Company Template on Netlify + Gumroad**
