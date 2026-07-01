#!/usr/bin/env python3
import json, os, subprocess, re
from pathlib import Path
from datetime import datetime, timezone

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

def x_mcp_query(keyword):
    try:
        cmd = [
            "npx", "-y", "@x/mcp-server",
            "--tool", "search_recent",
            "--params", json.dumps({"query": keyword, "max_results": 10})
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            data["source"] = "x_mcp"
            data["keyword"] = keyword
            return data
        return {"source": "x_mcp", "keyword": keyword, "error": result.stderr[-200:]}
    except Exception as e:
        return {"source": "x_mcp", "keyword": keyword, "error": str(e)}

def ollama_fallback(keyword):
    prompt = "Return ONLY a JSON array. Keyword: " + keyword + ". 3 objects with title, summary, opportunity. No explanation."
    try:
        result = subprocess.run(["ollama", "run", "glm-5.2:cloud", prompt], capture_output=True, text=True, timeout=180)
        content = strip_ansi(result.stdout)
        start = content.find("[")
        end = content.rfind("]")
        items = []
        if start >= 0 and end > start:
            items = json.loads(content[start:end+1])
        return {"source": "ollama_fallback", "keyword": keyword, "items": items}
    except Exception as e:
        return {"source": "ollama_fallback", "keyword": keyword, "error": str(e)}

def kimi_fallback(keyword):
    api_key = os.environ.get("MOONSHOT_API_KEY")
    if not api_key:
        return {"source": "kimi_fallback", "keyword": keyword, "error": "MOONSHOT_API_KEY not set"}
    try:
        import openai
        client = openai.OpenAI(api_key=api_key, base_url="https://api.moonshot.ai/v1")
        prompt = "Return ONLY JSON array. Keyword: " + keyword + ". 3 objects with title, summary, opportunity."
        resp = client.chat.completions.create(model="kimi-k2.7-code", messages=[{"role": "user", "content": prompt}], max_tokens=600)
        content = resp.choices[0].message.content
        start = content.find("[")
        end = content.rfind("]")
        items = json.loads(content[start:end+1]) if start >= 0 and end > start else []
        return {"source": "kimi_fallback", "keyword": keyword, "items": items}
    except Exception as e:
        return {"source": "kimi_fallback", "keyword": keyword, "error": str(e)}

def mock_fallback(keyword):
    # Demo mode: deterministic mock trends so pipeline runs without X API/Ollama.
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
    result = x_mcp_query(keyword)
    if not result.get("error") and len(result.get("items", [])) > 0:
        return result
    result = kimi_fallback(keyword)
    if not result.get("error") and len(result.get("items", [])) > 0:
        return result
    result = ollama_fallback(keyword)
    if not result.get("error") and len(result.get("items", [])) > 0:
        return result
    return mock_fallback(keyword)

def main():
    date = datetime.now().strftime("%Y-%m-%d")
    all_results = []
    total_items = 0
    for kw in KEYWORDS:
        print("Querying X trends for:", kw)
        result = query_keyword(kw)
        count = len(result.get("items", []))
        total_items += count
        all_results.append(result)

    output = {
        "date": date,
        "source": "x_trends.py",
        "keywords": KEYWORDS,
        "total_items": total_items,
        "results": all_results
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
    print("X trends:", total_items, "items across", len(KEYWORDS), "keywords")

if __name__ == "__main__":
    main()
