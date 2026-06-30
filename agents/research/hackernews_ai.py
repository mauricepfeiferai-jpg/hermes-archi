#!/usr/bin/env python3
"""Fetch AI-related stories from Hacker News top stories."""
import json
import urllib.request

def main():
    try:
        top = json.loads(urllib.request.urlopen("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10).read())
        stories = []
        keywords = ["ai", "llm", "agent", "claude", "gpt", "model"]
        for sid in top[:30]:
            story = json.loads(urllib.request.urlopen(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=10).read())
            if story and any(k in (story.get("title", "") + story.get("text", "")).lower() for k in keywords):
                stories.append({"title": story.get("title"), "url": story.get("url"), "score": story.get("score")})
        print(json.dumps({"source": "hackernews_ai", "count": len(stories), "items": stories[:5]}))
    except Exception as e:
        print(json.dumps({"source": "hackernews_ai", "count": 0, "error": str(e)}))

if __name__ == "__main__":
    main()
