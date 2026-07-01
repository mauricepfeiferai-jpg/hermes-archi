#!/usr/bin/env python3
"""Read-only connector for Apple Messages. Never sends messages."""
import argparse
import json
import subprocess


def messages_running() -> bool:
    result = subprocess.run(["pgrep", "-x", "Messages"], capture_output=True, text=True)
    return result.returncode == 0


def run_jxa(script: str) -> tuple[int, str, str]:
    result = subprocess.run(
        ["osascript", "-l", "JavaScript", "-e", script],
        capture_output=True, text=True, timeout=10
    )
    return result.returncode, result.stdout, result.stderr


def read_messages(limit: int = 10) -> dict:
    """Return recent messages from Apple Messages (chats)."""
    if not messages_running():
        return {"success": True, "source": "messages", "running": False, "count": 0, "messages": [], "note": "Messages.app is not running"}

    # Privacy note: returns sender handle and first 120 chars of content only.
    script = f'''
function run() {{
    try {{
        var Messages = Application("Messages");
        var chats = Messages.chats();
        var out = [];
        for (var ci = 0; ci < chats.length && out.length < {limit}; ci++) {{
            try {{
                var chat = chats[ci];
                var msgs = chat.messages();
                if (msgs.length === 0) continue;
                var m = msgs[msgs.length - 1];
                var text = m.text();
                if (text && text.length > 120) text = text.substring(0, 120) + "…";
                out.push({{
                    chatId: chat.id(),
                    handle: m.handle() || "me",
                    date: m.dateSent() ? m.dateSent().toISOString() : null,
                    preview: text || ""
                }});
            }} catch(err) {{
                // skip unreadable chats
            }}
        }}
        return JSON.stringify({{success: true, source: "messages", running: true, count: out.length, messages: out}});
    }} catch(err) {{
        var msg = err.toString();
        if (/läuft nicht|not running|isn.t running|-600/i.test(msg)) {{
            return JSON.stringify({{success: true, source: "messages", running: false, count: 0, messages: [], note: msg}});
        }}
        return JSON.stringify({{success: false, source: "messages", error: msg}});
    }}
}}
'''
    rc, out, err = run_jxa(script)
    if rc != 0:
        err_msg = err.strip() or "JXA failed"
        if any(k in err_msg.lower() for k in ["läuft nicht", "not running", "-600"]):
            return {"success": True, "source": "messages", "running": False, "count": 0, "messages": [], "note": err_msg}
        return {"success": False, "source": "messages", "error": err_msg}
    try:
        data = json.loads(out.strip())
        if not data.get("success") and any(k in (data.get("error") or "").lower() for k in ["läuft nicht", "not running", "-600"]):
            return {"success": True, "source": "messages", "running": False, "count": 0, "messages": [], "note": data.get("error")}
        return data
    except Exception as e:
        return {"success": False, "source": "messages", "error": f"JSON parse error: {e}", "raw": out.strip()}


def main() -> None:
    parser = argparse.ArgumentParser(description="MQC Apple Messages read-only connector")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = read_messages(limit=args.limit)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Messages: {result.get('count')} recent chats")
        for m in result.get("messages", [])[:args.limit]:
            print(f"- [{m.get('date', '?')}] {m.get('handle', '?')}: {m.get('preview', '')}")


if __name__ == "__main__":
    main()
