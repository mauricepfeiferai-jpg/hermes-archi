#!/usr/bin/env python3
"""Build a standalone dashboard HTML that works via file:// or http://.

Embeds data.json as window.DASHBOARD_DATA so fetch failures (file:// CORS)
fallback to inline data.
"""
import json, re
from pathlib import Path

HTML = Path("index.html")
text = HTML.read_text()

# Remove any previously embedded DASHBOARD_DATA block
pattern = r'\s*<script>\s*window\.DASHBOARD_DATA\s*=\s*\{.*?\};\s*</script>'
text = re.sub(pattern, "", text, flags=re.DOTALL)

data = json.loads(Path("data.json").read_text())
inline = f"""
  <script>
    window.DASHBOARD_DATA = {json.dumps(data, ensure_ascii=False)};
  </script>
"""

# Insert right before the main <script> that contains loadData
text = text.replace(
    "  <script>\n    async function loadData() {",
    inline + "\n  <script>\n    async function loadData() {"
)

# Ensure loadData has fallback
old_load = '''    async function loadData() {
      try {
        const res = await fetch('data.json');
        return res.ok ? await res.json() : null;
      } catch (e) { return null; }
    }'''

new_load = '''    async function loadData() {
      try {
        // Try to fetch fresh data when served over HTTP
        const res = await fetch('data.json');
        if (res.ok) return await res.json();
      } catch (e) {
        // file:// protocol or missing file: fall back to inline data
        console.log('fetch data.json failed, using embedded data:', e?.message || e);
      }
      // Embedded at build time so the dashboard works when opened directly
      return window.DASHBOARD_DATA || null;
    }'''

text = text.replace(old_load, new_load)

HTML.write_text(text)
print(f"Built standalone dashboard: {HTML}")
print(f"Embedded data.json generated_at: {data.get('generated_at')}")

if __name__ == "__main__":
    pass
