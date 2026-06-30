#!/usr/bin/env python3
"""Fetch latest AI papers from arXiv cs.AI RSS."""
import json
import urllib.request
import xml.etree.ElementTree as ET

def main():
    try:
        url = "http://export.arxiv.org/rss/cs.AI"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
        root = ET.fromstring(data)
        papers = []
        for item in root.iter("item"):
            title = item.find("title")
            link = item.find("link")
            if title is not None and link is not None:
                papers.append({"title": title.text.strip(), "link": link.text.strip()})
        print(json.dumps({"source": "arxiv_ai", "count": len(papers), "items": papers[:5]}))
    except Exception as e:
        print(json.dumps({"source": "arxiv_ai", "count": 0, "error": str(e)}))

if __name__ == "__main__":
    main()
