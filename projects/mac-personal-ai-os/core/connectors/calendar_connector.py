#!/usr/bin/env python3
"""Read-only connector for Apple Calendar. Never creates/edits events."""
import argparse
import json
import subprocess
import threading


def run_jxa(script: str, timeout: float = 8.0) -> tuple[int, str, str]:
    """Run JXA with a hard timeout; Calendar enumeration can be slow."""
    result = {"rc": -1, "out": "", "err": "", "timed_out": False}
    proc = None

    def target():
        nonlocal proc
        proc = subprocess.Popen(
            ["osascript", "-l", "JavaScript", "-e", script],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        out, err = proc.communicate()
        result["rc"] = proc.returncode
        result["out"] = out
        result["err"] = err

    t = threading.Thread(target=target)
    t.start()
    t.join(timeout)
    if t.is_alive() and proc:
        proc.kill()
        t.join()
        result["timed_out"] = True
        result["err"] = "Calendar query timed out (too many events or Calendar.app not responding)"

    return result["rc"], result["out"], result["err"], result["timed_out"]


def read_calendar(days: int = 1, limit_per_cal: int = 20) -> dict:
    """Return calendar events from now until +days using JXA whose filter."""
    script = f'''
function run() {{
    var Calendar = Application("Calendar");
    var now = new Date();
    var end = new Date(now.getTime() + {days} * 24 * 60 * 60 * 1000);
    var cals = Calendar.calendars();
    var out = [];
    for (var ci = 0; ci < cals.length; ci++) {{
        try {{
            var cal = cals[ci];
            var events = cal.events.whose({{
                _and: [
                    {{startDate: {{_greaterThanEquals: now}}}},
                    {{startDate: {{_lessThanEquals: end}}}}
                ]
            }});
            var total = events.length;
            if (total > {limit_per_cal}) total = {limit_per_cal};
            for (var i = 0; i < total; i++) {{
                var e = events[i];
                out.push({{
                    calendar: cal.title(),
                    title: e.summary(),
                    start: e.startDate().toISOString(),
                    end: e.endDate() ? e.endDate().toISOString() : null,
                    allDay: e.alldayEvent(),
                    location: e.location() || ""
                }});
            }}
        }} catch(err) {{
            out.push({{calendar: cal.title ? cal.title() : "Unknown", error: err.toString()}});
        }}
    }}
    out.sort(function(a, b) {{
        if (!a.start) return 1;
        if (!b.start) return -1;
        return new Date(a.start) - new Date(b.start);
    }});
    return JSON.stringify({{success: true, source: "calendar", window_days: {days}, count: out.length, events: out}});
}}
'''
    rc, out, err, timed_out = run_jxa(script)
    if timed_out:
        return {"success": False, "source": "calendar", "degraded": True, "error": err}
    if rc != 0:
        return {"success": False, "source": "calendar", "error": err.strip() or "JXA failed"}
    try:
        return json.loads(out.strip())
    except Exception as e:
        return {"success": False, "source": "calendar", "error": f"JSON parse error: {e}", "raw": out.strip()}


def main() -> None:
    parser = argparse.ArgumentParser(description="MQC Apple Calendar read-only connector")
    parser.add_argument("--days", type=int, default=1, help="Look-ahead window in days")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = read_calendar(days=args.days)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Calendar: {result.get('count')} events in next {args.days} day(s)")
        for e in result.get("events", [])[:20]:
            print(f"- [{e.get('start', '?')}] {e.get('title', '?')} @ {e.get('location', '?') or 'no location'}")


if __name__ == "__main__":
    main()
