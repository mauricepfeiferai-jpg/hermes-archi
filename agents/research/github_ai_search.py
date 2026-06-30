#!/usr/bin/env python3
"""Fetch recent AI agent repos from GitHub search API (no auth)."""
import json
import urllib.request
from datetime import datetime, timedelta
import sys

AI_KEYWORDS = ["ai", "agent", "llm", "gpt", "claude", "automation", "mcp", "prompt", "workflow", "model", "coding", "vision", "multimodal", "agency", "orchestration", "self-improving"]

def main():
    try:
        since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        url = f"https://api.github.com/search/repositories?q=ai+agent+created:%3E{since}&sort=stars&order=desc&per_page=15"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = json.loads(urllib.request.urlopen(req, timeout=15).read().decode("utf-8"))
        repos = []
        for item in data.get("items", []):
            name = item.get("full_name", "")
            desc = (item.get("description") or "")[:160]
            stars = item.get("stargazers_count", 0)
            url_repo = item.get("html_url", "")
            parts = name.split("/")
            if len(parts) == 2:
                owner, repo = parts
                if any(k in (repo + " " + desc).lower() for k in AI_KEYWORDS):
                    repos.append({"owner": owner, "repo": repo, "hint": desc, "stars": stars, "url": url_repo})
        if len(repos) < 3:
            for item in data.get("items", [])[:5]:
                name = item.get("full_name", "")
                desc = (item.get("description") or "")[:160]
                stars = item.get("stargazers_count", 0)
                url_repo = item.get("html_url", "")
                parts = name.split("/")
                if len(parts) == 2:
                    owner, repo = parts
                    if not any(r.get("owner") == owner and r.get("repo") == repo for r in repos):
                        repos.append({"owner": owner, "repo": repo, "hint": desc, "stars": stars, "url": url_repo})
        print(json.dumps({"source": "github_search", "count": len(repos), "items": repos[:15]}))
    except Exception as e:
        print(json.dumps({"source": "github_search", "count": 0, "error": str(e)}))

if __name__ == "__main__":
    main()
