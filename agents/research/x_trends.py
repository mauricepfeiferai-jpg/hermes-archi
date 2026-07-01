#!/usr/bin/env python3
"""Free X/Twitter trend ingest for Hermes/Hecate.

No X API key, no paid API. Uses free sources:
- GitHub Search API (AI repos, code trends)
- Hacker News RSS (tech discussions)
- arXiv cs.AI RSS (research trends)
- Kimi / Ollama synthesis (generate trend theses from collected data)
- Deterministic mock fallback (pipeline always runs)

Optional: Agent Reach twitter-cli with cookie (when available).
"""
import json, os, re, subprocess
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote

import requests

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"
OUT_DIR = REPO / "state" / "x"
OUT_DIR.mkdir(parents=True, exist_ok=True)

KEYWORDS = [
    "AI agent", "solopreneur", "one person business", "Claude Code",
    "OpenClaw", "Grok", "MCP server", "AI startup"
]

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def strip_ansi(text):
    return ANSI_RE.sub("", text)


def github_search_trends(keyword):
    """Search GitHub for trending repos matching keyword."""
    try:
        q = quote(keyword)
        url = f"https://api.github.com/search/repositories?q={q}+created:%3E2024-01-01&sort=stars&order=desc&per_page=5"
        r = requests.get(url, timeout=20, headers={"Accept": "application/vnd.github.v3+json"})
        if r.status_code != 200:
            return {"source": "github", "keyword": keyword, "error": f"status {r.status_code}"}
        items = []
        for item in r.json().get("items", [])[:5]:
            items.append({
                "title": item.get("full_name", ""),
                "summary": item.get("description") or "No description",
                "opportunity": f"Repo: {item.get('html_url', '')} ({item.get('stargazers_count', 0)} stars)",
                "url": item.get("html_url", ""),
            })
        return {"source": "github", "keyword": keyword, "items": items}
    except Exception as e:
        return {"source": "github", "keyword": keyword, "error": str(e)}


def hn_rss_trends(keyword):
    """Hacker News newest items; filter by keyword relevance."""
    try:
        url = "https://hnrss.org/newest?count=50"
        import feedparser
        d = feedparser.parse(url)
        items = []
        kw_lower = keyword.lower()
        for e in d.entries:
            title = e.get("title", "")
            if kw_lower in title.lower():
                items.append({
                    "title": title[:120],
                    "summary": e.get("summary", "")[:200],
                    "opportunity": f"HN: {e.get('link', '')}",
                    "url": e.get("link", ""),
                })
            if len(items) >= 3:
                break
        return {"source": "hackernews", "keyword": keyword, "items": items}
    except Exception as e:
        return {"source": "hackernews", "keyword": keyword, "error": str(e)}


def arxiv_rss_trends(keyword):
    """arXiv cs.AI latest; filter by keyword."""
    try:
        url = "http://export.arxiv.org/rss/cs.AI"
        import feedparser
        d = feedparser.parse(url)
        items = []
        kw_lower = keyword.lower()
        for e in d.entries[:30]:
            title = e.get("title", "")
            if kw_lower in title.lower():
                items.append({
                    "title": title[:120],
                    "summary": e.get("summary", "")[:200],
                    "opportunity": f"arXiv: {e.get('link', '')}",
                    "url": e.get("link", ""),
                })
            if len(items) >= 3:
                break
        return {"source": "arxiv", "keyword": keyword, "items": items}
    except Exception as e:
        return {"source": "arxiv", "keyword": keyword, "error": str(e)}


def agent_reach_twitter_search(keyword):
    """Optional: Agent Reach twitter-cli if cookie configured."""
    agent_reach = Path.home() / ".openclaw" / "workspace" / "ai-empire" / "09_LIBRARY" / "github" / "agent-reach" / ".venv" / "bin" / "twitter"
    if not agent_reach.exists():
        return {"source": "agent_reach_twitter", "keyword": keyword, "error": "twitter CLI not installed"}
    try:
        result = subprocess.run(
            [str(agent_reach), "search", keyword, "--limit", "5"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return {"source": "agent_reach_twitter", "keyword": keyword, "error": strip_ansi(result.stderr[-200:])}
        text = strip_ansi(result.stdout)
        # Heuristic: split by tweet separators and extract lines
        tweets = []
        for block in re.split(r"\n\n+", text):
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if lines:
                tweets.append({
                    "title": lines[0][:120],
                    "summary": " ".join(lines[1:])[:200],
                    "opportunity": "X/Twitter via Agent Reach",
                    "url": "",
                })
        return {"source": "agent_reach_twitter", "keyword": keyword, "items": tweets[:5]}
    except Exception as e:
        return {"source": "agent_reach_twitter", "keyword": keyword, "error": str(e)}


def kimi_synthesize(keyword, collected_items):
    """Use Kimi to synthesize 3 trend theses from collected free sources."""
    api_key = os.environ.get("MOONSHOT_API_KEY")
    if not api_key:
        return {"source": "kimi_synthesize", "keyword": keyword, "error": "MOONSHOT_API_KEY not set"}
    try:
        import openai
        client = openai.OpenAI(api_key=api_key, base_url="https://api.moonshot.ai/v1")
        context = "\n".join(
            f"- {it.get('title', '')}: {it.get('summary', '')}"
            for src in collected_items
            for it in src.get("items", [])
        )
        prompt = f"""Keyword: {keyword}
Based ONLY on the following collected items, return a JSON array of 3 trend theses.
Each object must have: title, summary, opportunity.
Collected items:
{context[:2000]}

Return ONLY a JSON array. No explanation."""
        resp = client.chat.completions.create(
            model="kimi-k2.7-code",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            timeout=20,
        )
        content = resp.choices[0].message.content
        start = content.find("[")
        end = content.rfind("]")
        items = json.loads(content[start:end + 1]) if start >= 0 and end > start else []
        return {"source": "kimi_synthesize", "keyword": keyword, "items": items}
    except Exception as e:
        return {"source": "kimi_synthesize", "keyword": keyword, "error": str(e)}



def mock_fallback(keyword):
    """Demo mode: deterministic mock trends so pipeline runs without any API."""
    trends = {
        "AI agent": [
            {"title": "Autonomous Coding Agents", "summary": "Agents that plan, write, test and deploy code end-to-end.", "opportunity": "Dev-tool templates and agent-as-a-service platforms."},
            {"title": "Multi-Agent Orchestration", "summary": "Specialized agents collaborating via shared memory and bus.", "opportunity": "Enterprise workflow automation playbooks."},
            {"title": "Computer-Use Agents", "summary": "Agents controlling browser and desktop GUIs directly.", "opportunity": "Automated QA, scraping and digital-assistant products."}
        ],
        "solopreneur": [
            {"title": "One-Person AI Companies", "summary": "Founders running product, sales and ops with agents.", "opportunity": "OS templates and coaching for solo founders."},
            {"title": "AI Content Systems", "summary": "Loops that research, write, edit and post without the founder.", "opportunity": "Done-for-you content operations."},
            {"title": "No-Hiring Growth", "summary": "Revenue scaling before first employee via agent teams.", "opportunity": "Agency and consulting services."}
        ],
        "one person business": [
            {"title": "Agent-Human Hybrid", "summary": "One human plus five agents equals a full team.", "opportunity": "Training programs and tool stacks."},
            {"title": "Micro-SaaS Agents", "summary": "Agents building and maintaining tiny SaaS products.", "opportunity": "Micro-SaaS boilerplates."},
            {"title": "Personal AI Brain", "summary": "Wiki + skills + memory become competitive moat.", "opportunity": "Second-brain migration services."}
        ],
        "Claude Code": [
            {"title": "Claude Code Loops", "summary": "Developers running edit/test/verify/memory loops.", "opportunity": "Loop engineering templates and courses."},
            {"title": "Claude Skills Marketplace", "summary": "Reusable skills for specific stacks and workflows.", "opportunity": "Skill packs for common SaaS tasks."},
            {"title": "Claude + MCP", "summary": "Connecting Claude to databases, APIs and browsers via MCP.", "opportunity": "MCP connector packs."}
        ],
        "OpenClaw": [
            {"title": "OpenClaw Mobile Agents", "summary": "Agent OS accessible from iOS and Android.", "opportunity": "Mobile-first agent workflows."},
            {"title": "OpenClaw Channels", "summary": "Routing agent replies to Telegram, Slack, WhatsApp.", "opportunity": "Notification and delivery automation."},
            {"title": "OpenClaw Local Models", "summary": "Running local models without cloud dependency.", "opportunity": "Privacy-first agent stacks."}
        ],
        "Grok": [
            {"title": "Grok Real-Time Search", "summary": "Using live X signal for research and content.", "opportunity": "Real-time trend dashboards."},
            {"title": "Grok Image Analysis", "summary": "Multimodal reasoning over charts and UI.", "opportunity": "Automated design/code review agents."},
            {"title": "Grok API Workflows", "summary": "Developers wiring Grok into agent stacks.", "opportunity": "Grok integration playbooks."}
        ],
        "MCP server": [
            {"title": "MCP Ecosystem", "summary": "Every major platform shipping an MCP server.", "opportunity": "MCP server directories and tutorials."},
            {"title": "X MCP Launch", "summary": "X/Twitter real-time signal now available via MCP.", "opportunity": "Social-listening agent products."},
            {"title": "MCP + Skills", "summary": "Skills calling MCP tools declaratively.", "opportunity": "Reusable skill packs."}
        ],
        "AI startup": [
            {"title": "Vibe Coding", "summary": "Founders shipping products via agent loops.", "opportunity": "Vibe-coding bootcamps and templates."},
            {"title": "AI-Native SDLC", "summary": "Triage, spec, code, verify and deploy by agents.", "opportunity": "Factory engineering products."},
            {"title": "Cheap AI Stacks", "summary": "Chinese models and local inference cutting costs 87%.", "opportunity": "Cost-optimization playbooks."}
        ]
    }
    return {"source": "mock_demo", "keyword": keyword, "items": trends.get(keyword, [])}


def query_keyword(keyword):
    """Collect free sources, synthesize, fallback chain."""
    collected = []

    # Free tier sources
    for source_fn in [github_search_trends, hn_rss_trends, arxiv_rss_trends]:
        result = source_fn(keyword)
        if not result.get("error") and result.get("items"):
            collected.append(result)

    # Optional Agent Reach twitter cookie (usually fails without cookie)
    tw = agent_reach_twitter_search(keyword)
    if not tw.get("error") and tw.get("items"):
        collected.append(tw)

    # Synthesis if we have collected data
    if collected:
        result = kimi_synthesize(keyword, collected)
        if not result.get("error") and result.get("items"):
            collected.append(result)
            return {
                "keyword": keyword,
                "sources": collected,
                "synthesized": result,
                "items": result.get("items", []),
            }

    # Fallback: if any free source returned items, return them directly
    if collected:
        return {
            "keyword": keyword,
            "sources": collected,
            "synthesized": None,
            "items": [it for src in collected for it in src.get("items", [])][:5],
        }

    # Last resort: deterministic mock
    mock = mock_fallback(keyword)
    return {
        "keyword": keyword,
        "sources": [mock],
        "synthesized": None,
        "items": mock.get("items", []),
    }


def main():
    date = datetime.now().strftime("%Y-%m-%d")
    all_results = []
    total_items = 0
    for kw in KEYWORDS:
        print("Querying free trends for:", kw)
        result = query_keyword(kw)
        count = len(result.get("items", []))
        total_items += count
        all_results.append(result)

    output = {
        "date": date,
        "source": "x_trends.py (free ingest)",
        "keywords": KEYWORDS,
        "total_items": total_items,
        "results": all_results,
    }
    outfile = OUT_DIR / ("trends_" + date + ".json")
    outfile.write_text(json.dumps(output, indent=2))

    bus_dir = REPO / "state" / "neural-bus"
    bus_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    event = {
        "ts": now.isoformat().replace("+00:00", "Z"),
        "type": "x.trends.discovered",
        "source": "x_trends.py",
        "payload": {"file": str(outfile), "items": total_items, "keywords": len(KEYWORDS)},
        "recipients": ["emperor", "writer", "researcher", "openclaw_main"]
    }
    ts = now.isoformat().replace("+00:00", "Z").replace(":", "-").replace(".", "-")
    (bus_dir / (ts + "_x.trends.discovered.json")).write_text(json.dumps(event, indent=2))
    print("Free trends:", total_items, "items across", len(KEYWORDS), "keywords")
    print("Saved to:", outfile)


if __name__ == "__main__":
    main()
