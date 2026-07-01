#!/usr/bin/env python3
"""MQC web search via DuckDuckGo (ddgs). Free, no API key, no Docker."""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    from ddgs import DDGS
except ImportError as exc:  # pragma: no cover
    print(json.dumps({"error": f"ddgs not installed: {exc}"}, ensure_ascii=False))
    sys.exit(1)

# German / English search prefixes we strip so the raw query reaches the index
STRIP_PREFIXES = [
    r"^suche nach\b",
    r"^suche im web\b",
    r"^web suche\b",
    r"^google nach\b",
    r"^duckduckgo\b",
    r"^recherchiere\b",
    r"^recherche im internet\b",
    r"^finde\b",
    r"^look up\b",
    r"^search the web\b",
    r"^search for\b",
]


def clean_query(raw: str) -> str:
    q = raw.strip()
    for pattern in STRIP_PREFIXES:
        q = re.sub(pattern, "", q, flags=re.IGNORECASE).strip()
    # Collapse leftover leading punctuation
    q = re.sub(r"^[,:;\-]+\s*", "", q)
    return q or raw.strip()


def search(query: str, max_results: int = 5, region: str = "de-de", safesearch: str = "moderate") -> dict:
    """Run a DuckDuckGo text search and return structured results."""
    query = clean_query(query)
    try:
        with DDGS() as ddgs:
            raw = ddgs.text(query, max_results=max_results, region=region, safesearch=safesearch)
    except Exception as exc:
        return {"success": False, "query": query, "error": str(exc)}

    results = []
    for item in raw:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("href", ""),
            "snippet": item.get("body", ""),
        })
    return {
        "success": True,
        "query": query,
        "backend": "ddgs",
        "count": len(results),
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="MQC DuckDuckGo web search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max-results", type=int, default=5, help="Number of results (default 5)")
    parser.add_argument("--region", default="de-de", help="DuckDuckGo region (default de-de)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = search(args.query, max_results=args.max_results, region=args.region)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Query: {result.get('query')}")
        print(f"Backend: {result.get('backend')} | Results: {result.get('count')}")
        if not result.get("success"):
            print(f"Error: {result.get('error')}")
            sys.exit(1)
        for i, r in enumerate(result.get("results", []), 1):
            print(f"\n{i}. {r['title']}\n   {r['url']}\n   {r['snippet'][:200]}")


if __name__ == "__main__":
    main()
