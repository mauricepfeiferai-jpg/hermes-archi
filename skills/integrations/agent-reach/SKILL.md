---
name: agent-reach-integration
title: Agent Reach Integration — Internet Access for AI Agents
description: "Hermes skill for safely integrating Agent Reach (Panniantong/Agent-Reach) — a tool that gives AI agents access to YouTube, Twitter/X, Reddit, Bilibili, Xiaohongshu, web search, and more. Use only after security review and in isolated environments. Never auto-install into production systems or extract browser cookies without explicit approval."
version: 1.0.0
author: AI Empire
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [Agent-Reach, Internet-Access, Web-Scraping, MCP, Social-Media, Chinese-Stack]
    category: integrations
    requires_toolsets: [terminal, file]
---

# Agent Reach Integration

## What It Is

Agent Reach (https://github.com/Panniantong/Agent-Reach) gives AI agents the ability to read/search:

- Web pages (Jina Reader)
- YouTube (subtitles, search)
- Twitter/X (single tweets, search, timeline)
- Reddit (search, posts, comments)
- Bilibili (search, video details)
- Xiaohongshu/RED (search, read, comments)
- Facebook, Instagram, LinkedIn (with browser login)
- GitHub, RSS, V2EX, Xueqiu, Xiaoyuzhou podcast

## Staged Location

`~/.openclaw/workspace/ai-empire/09_LIBRARY/github/agent-reach`

## Safety Rules

1. **Never auto-install into system Python.** Always use a dedicated venv.
2. **Never extract browser cookies without explicit approval.** This is a privacy/security boundary.
3. **Run `agent-reach doctor` first** to see what would be installed/changed.
4. **Use `--dry-run` and `--safe` flags** before any real install.
5. **Prefer local laptop over server** for cookie-requiring platforms.
6. **Keep it isolated from Hermes Gateway / OpenClaw Gateway until proven safe.**
7. **Do not enable all channels by default.** Enable one at a time.

## Recommended First Steps

1. Create isolated venv:
   ```bash
   python3 -m venv ~/.venvs/agent-reach
   source ~/.venvs/agent-reach/bin/activate
   ```

2. Install in dry-run mode:
   ```bash
   cd ~/.openclaw/workspace/ai-empire/09_LIBRARY/github/agent-reach
   pip install -e . --dry-run
   ```

3. Run doctor:
   ```bash
   agent-reach doctor
   ```

4. Enable only zero-config channels first:
   - web reader
   - YouTube
   - RSS
   - V2EX
   - Xueqiu

5. Test one channel at a time with a harmless query.

## Integration with AI Empire

### Use-Cases

- **Content Blitz / Post-X:** Get Twitter/X data, Reddit discussions, YouTube transcripts for content ideas.
- **Researcher Agent:** Web search + platform scanning for market research.
- **Chinese AI Stack:** Access Chinese platforms (Bilibili, Xiaohongshu) without API keys.
- **BMA Service:** Monitor German fire-safety discussions? (likely low value — evaluate first).

### Channels to Enable First

| Channel | Config Effort | Value for AI Empire |
|---|---|---|
| Web Reader | None | High |
| YouTube | None | High |
| RSS | None | Medium |
| GitHub | Token optional | High |
| Twitter/X | Cookie/login | High |
| Reddit | Cookie/login | Medium |
| Bilibili | None | Medium |
| Xiaohongshu | Cookie/login | Low-Medium |

### Channels to Skip / Evaluate Later

- Facebook, Instagram, LinkedIn profile scraping (legal/privacy risk)
- Any channel requiring server proxy with credentials

## Connection to Existing Products

- **Content Blitz Skill** can use Agent Reach for sourcing.
- **Post-X Skill** can use Agent Reach for Twitter data.
- **YouTube Automation Skill** can use Agent Reach for transcripts.
- **Chinese AI Stack Migration** strategy aligns with Agent Reach's China-platform focus.

## Templates

- `assets/INSTALL_CHECKLIST.md`
- `assets/SECURITY_GATES.md`
