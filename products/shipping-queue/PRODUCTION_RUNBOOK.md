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

---

## Status Update — 2026-06-29 21:38

### Done
- 20-agent hybrid swarm activated across 5 tmux windows
- Top product landing page rebuilt with full copy, pricing, comparison table
- Product index page rebuilt with 6 clean product cards
- Deliverable zip created: `releases/one-person-ai-agent-company-template.zip`
- Changes committed and pushed to GitHub (main branch)
- Netlify Drop zip regenerated: `/tmp/ai-empire-products-drop.zip`

### Blockers
1. GitHub Actions workflow cannot be pushed — OAuth token lacks `workflow` scope
2. GitHub Pages will not deploy from a private repo on a free plan
3. Netlify CLI auto-deploy needs `NETLIFY_AUTH_TOKEN`

### Next User Actions
1. Fastest live URL: open https://app.netlify.com/drop and drag `/tmp/ai-empire-products-drop.zip`
2. For auto-deploy: provide `NETLIFY_AUTH_TOKEN` or run `gh auth refresh --scopes repo,workflow` and make repo public
3. Upload `releases/one-person-ai-agent-company-template.zip` to Gumroad as the $149 Professional product

### What Works Right Now
- Landing page files are in GitHub: `website/products/one-person-ai-agent-company.html`
- Deliverable zip is in GitHub: `releases/one-person-ai-agent-company-template.zip`
- Product is ready to list and sell

---

## Status Update — 2026-06-29 21:42

### LIVE ✅
- **Production URL:** https://coruscating-daffodil-e6bc5f.netlify.app
- **Index page:** 200 OK
- **One-Person AI Agent Company page:** 200 OK
- **Netlify site name:** coruscating-daffodil-e6bc5f
- **Admin URL:** https://app.netlify.com/projects/coruscating-daffodil-e6bc5f

### Next Step
Upload `releases/one-person-ai-agent-company-template.zip` to Gumroad as $149 Professional tier and update the Gumroad link in:
- `website/products/one-person-ai-agent-company.html`
- Product index (optional)

---

## Status Update — 2026-06-29 22:05

### Content Ready
- X/Twitter launch thread: `products/one-person-ai-agent-company/go-to-market/launch-content/X_THREAD_LAUNCH.md`
- LinkedIn launch post: `products/one-person-ai-agent-company/go-to-market/launch-content/LINKEDIN_POST_LAUNCH.md`
- LinkedIn cold DM template: `products/one-person-ai-agent-company/go-to-market/launch-content/COLD_DM_LINKEDIN.md`
- Launch checklist: `products/one-person-ai-agent-company/go-to-market/launch-content/LAUNCH_CHECKLIST.md`
- OG image: ✅ Live at https://coruscating-daffodil-e6bc5f.netlify.app/assets/og-image.png

### Still Blocking Full Launch
- Gumroad product listing needs real buy link
- Once Gumroad link exists, update `website/products/one-person-ai-agent-company.html` CTA buttons

---

## Status Update — 2026-06-29 22:18

### Template Is Now Runnable
- 7 agent roles with full job descriptions
- 10 executable cron scripts with crontab
- Daily review + retro + self-improve loop
- Hermes CLI wiring via `ops/cron/run_agent.py` (stub + fallback)
- BMA service-business variant for German fire-safety contractors
- Manual test cycle completed successfully
- Deliverable zip updated to 25KB

### Verified Commands
```bash
bash ops/cron/06-ceo-daily-goals.sh
bash ops/cron/07-cto-tech-health.sh
bash ops/cron/08-engineer-ship.sh
bash ops/cron/19-ops-backup-health.sh
bash loop/run_loop.sh
```

### Updated Deliverables
- `releases/one-person-ai-agent-company-template.zip` — 25KB
- Netlify site redeployed with latest assets
- GitHub repo pushed to main

### Still To Do Before Selling
- [ ] Create Gumroad product
- [ ] Upload deliverable zip to Gumroad
- [ ] Replace placeholder Gumroad link in landing page
- [ ] Post X thread + LinkedIn post


---

## Status Update — 2026-06-29 22:32 — GO LIVE APPROVED

### Completed
- Full smoke test passed
- Deliverable zip regenerated and clean (26KB, outputs excluded)
- `GO_LIVE_PACKAGE.md` created with soft-launch and hard-launch copy
- Memory files updated
- Landing page remains live: https://coruscating-daffodil-e6bc5f.netlify.app/one-person-ai-agent-company.html

### Pending User Choice
**Soft Launch (A)** — post now, collect "DM me" replies, no broken buy link.  
**Hard Launch (B)** — create Gumroad product first, then post with real link.

### I Cannot Do Automatically
- Post on X/LinkedIn (no API credentials configured)
- Create Gumroad product (requires login + upload)
- Collect payments

### I Will Do Next
After Maurice chooses A or B:
- A: finalize posts, commit/push, wait for user to copy-paste and post manually
- B: wait for Gumroad link, update landing page, redeploy, then provide final posts

---

## Status Update — 2026-06-29 23:14

### Latest Push
- Commit `dadbefb`: added 4 Claude Code loops framework to README + landing page
- Landing page now includes:
  - Dario Amodei quote (configuration beats seniority)
  - Morning action queue concept
  - Dashboard UI preview screenshot
  - 4 loops framework
  - YouTube Operator Agent
  - Spec Agent + Triage/Implement GitHub Actions
- Netlify redeployed successfully — all pages 200 OK
- Deliverable zip: 158KB

### Gold Nuggets Extracted (not in repo)
- Local Hermes + Qwen 3.6 + DGX Spark
- Morning action queue (Laurel CSM)
- Dario Amodei config quote
- 4 Claude Code loops
- YouTube Claude system (Big Chris)
- Spec-driven factory (Warp)
- Cloud software factory v1 (Warp)
- Agent Reach, Voicebox, BuilderIO agent-native, Anthropic cybersecurity skills

### Still Waiting
- Real Gumroad product link for hard launch

### Recommended Next Action
Create Gumroad product → send link → update CTA → finalize launch copy.
