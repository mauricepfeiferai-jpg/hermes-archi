"""SkillWriter — autonomous lesson → skill integration.

Any agent in Core4 can POST a lesson to Hermes /learn and it gets
written into the appropriate skill file. This is the self-improvement loop:
agent encounters something → learns → system gets smarter for next run.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

log = logging.getLogger("hermes.skill_writer")

SKILLS_DIR = Path(os.environ.get("CLAUDE_SKILLS_DIR", Path.home() / ".claude/skills"))


class SkillWriter:
    def write_lesson(self, skill_name: str, lesson: str, source_agent: str) -> dict:
        """Append a lesson to an existing skill file."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"

        if not skill_path.exists():
            # Create new skill stub
            skill_path.parent.mkdir(parents=True, exist_ok=True)
            skill_path.write_text(
                f"---\nname: {skill_name}\ndescription: Auto-created by {source_agent}\n---\n\n"
                f"# {skill_name}\n\nAuto-created {datetime.utcnow().date()}.\n"
            )
            log.info("Created new skill: %s", skill_name)

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        entry = f"\n\n---\n\n## Lesson from {source_agent} ({timestamp})\n\n{lesson.strip()}\n"

        with open(skill_path, "a") as f:
            f.write(entry)

        log.info("Lesson written to skill '%s' by %s (%d chars)", skill_name, source_agent, len(lesson))
        return {"ok": True, "skill": skill_name, "skill_path": str(skill_path), "chars": len(lesson)}

    def list_skills(self) -> list[str]:
        if not SKILLS_DIR.exists():
            return []
        return sorted(p.name for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").exists())
