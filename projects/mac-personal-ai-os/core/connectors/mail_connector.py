#!/usr/bin/env python3
"""Read-only connector for Apple Mail. Never sends mail."""
import argparse
import json
import subprocess
import sys


def run_jxa(script: str) -> tuple[int, str, str]:
    result = subprocess.run(
        ["osascript", "-l", "JavaScript", "-e", script],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode, result.stdout, result.stderr


def read_mail(limit: int = 10, unread_only: bool = True) -> dict:
    """Return recent unread (or all) mail messages from Apple Mail."""
    script = f'''
function run() {{
    var Mail = Application("Mail");
    var inbox = Mail.inbox();
    var messages = inbox.messages();
    var out = [];
    var count = 0;
    for (var i = 0; i < messages.length && count < {limit}; i++) {{
        var m = messages[i];
        if ({'true' if unread_only else 'false'} && m.readStatus()) continue;
        out.push({{
            id: m.id(),
            subject: m.subject(),
            sender: m.sender() ? m.sender().toString() : "Unknown",
            date: m.dateReceived() ? m.dateReceived().toISOString() : null,
            read: m.readStatus()
        }});
        count++;
    }}
    return JSON.stringify({{success: true, source: "mail", count: out.length, messages: out}});
}}
'''
    rc, out, err = run_jxa(script)
    if rc != 0:
        return {"success": False, "source": "mail", "error": err.strip() or "JXA failed"}
    try:
        return json.loads(out.strip())
    except Exception as e:
        return {"success": False, "source": "mail", "error": f"JSON parse error: {e}", "raw": out.strip()}


def main() -> None:
    parser = argparse.ArgumentParser(description="MQC Apple Mail read-only connector")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--all", action="store_true", dest="all_messages", help="Include read messages too")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = read_mail(limit=args.limit, unread_only=not args.all_messages)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Mail: {result.get('count')} messages")
        for m in result.get("messages", [])[:args.limit]:
            print(f"- [{m.get('date', '?')}] {m.get('sender', '?')}: {m.get('subject', '?')}")


if __name__ == "__main__":
    main()
