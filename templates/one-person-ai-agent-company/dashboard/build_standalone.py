#!/usr/bin/env python3
"""Build a standalone dashboard HTML that works via file:// or http://.

Embeds data.json as window.DASHBOARD_DATA AND pre-fills DOM values so the
dashboard renders correctly even if fetch/JS has issues.
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

# Normalize existing loadData to our robust version
load_pattern = r'\s*async function loadData\(\) \{.*?return window\.DASHBOARD_DATA \|\| null;\s*\}'
new_load = '''    async function loadData() {
      // Use embedded data by default. It is built at the same time as the HTML
      // and guarantees the dashboard works via file://, GitHub Pages, or cache.
      if (window.DASHBOARD_DATA) {
        // Optional: try to refresh from data.json in the background, but do not block
        try {
          const res = await fetch('data.json?_=' + Date.now());
          if (res.ok) {
            const fresh = await res.json();
            // If fresh data differs, re-render (only useful when served via HTTP)
            if (fresh && fresh.generated_at !== window.DASHBOARD_DATA.generated_at) {
              window.DASHBOARD_DATA = fresh;
              init();
            }
          }
        } catch (e) {
          // ignore: file://, offline, or cached old data
        }
        return window.DASHBOARD_DATA;
      }
      // Fallback for unbuilt HTML (should not happen after build_standalone.py)
      try {
        const res = await fetch('data.json?_=' + Date.now());
        if (res.ok) return await res.json();
      } catch (e) {}
      return null;
    }'''

text = re.sub(load_pattern, new_load, text, flags=re.DOTALL)

# Pre-fill DOM values from data so page shows correct numbers before/without JS
replacements = {
    'id="lessons-count"': f'>{data.get("lessons", 0)}<',
    'id="dopamine-score"': f'>{round(data.get("dopamine_score", 0))}<',
    'id="dopamine-streak"': f'>Streak: {data.get("dopamine_streak", 0)} days<',
    'id="neural-events"': f'>{data.get("neural_events", 0)}<',
    'id="library-count"': f'>{(data.get("github_repos", 0) + data.get("skills", 0) + data.get("knowledge_nuggets", 0))}<',
    'id="x-trends-count"': f'>{data.get("x_trends_24h", 0)}<',
    'id="x-trends-source"': f'>{"Live pipeline" if data.get("x_trends_24h", 0) > 0 else "Mock demo mode"}<',
    'id="hil-gate-checks"': f'>{data.get("hil_gate_checks", 0)}<',
    'id="sales-leads"': f'>{data.get("sales_leads", 0)}<',
    'id="sales-contacted"': f'>{data.get("sales_contacted", 0)}<',
    'id="sales-replied"': f'>{data.get("sales_replied", 0)}<',
    'id="sales-revenue"': f'>${round(data.get("sales_deals_value_usd", 0)):,}<',
}

for marker, new_tail in replacements.items():
    # Find the element with this marker and replace its first closing-content tag
    # e.g. <div class="value" id="dopamine-score">0</div>  -> replace only the ">0<"
    regex = rf'({re.escape(marker)}[^>]*?)\u003e[^\u003c]*\u003c'
    text = re.sub(regex, rf'\1{new_tail}', text, count=1)

# HIL summary special case
hil_red = data.get("hil_red_blocks", 0)
hil_yellow = data.get("hil_yellow", 0)
hil_green = data.get("hil_green", 0)
text = re.sub(
    r'id="hil-gate-summary"\u003e[^\u003c]*\u003c',
    f'id="hil-gate-summary"\u003eGREEN: {hil_green} · YELLOW: {hil_yellow} · RED: {hil_red}\u003c',
    text
)

# Backup age
text = re.sub(
    r'id="backup-age"[^\u003e]*\u003e[^\u003c]*\u003c',
    'id="backup-age" style="font-size: 22px; padding-top: 10px;"\u003eToday\u003c',
    text
)

HTML.write_text(text)
print(f"Built standalone dashboard: {HTML}")
print(f"Embedded data.json generated_at: {data.get('generated_at')}")
print(f"Pre-filled values from data.json")

if __name__ == "__main__":
    pass
