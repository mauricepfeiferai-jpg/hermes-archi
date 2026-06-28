"""Goal Store — YAML-backed Kanban-storage for goals."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.models import GoalCard, GoalStatus  # noqa: E402

log = logging.getLogger("hermes.goals")

# Goals folder (can be overridden via env)
GOALS_DIR = Path(os.getenv("GOALS_DIR",
                           Path(__file__).resolve().parents[2] / "control-plane" / "goals"))
ACTIVE_DIR = GOALS_DIR / "active"
ARCHIVE_DIR = GOALS_DIR / "archive"


class GoalStore:
    def __init__(self) -> None:
        ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, GoalCard] = {}
        self._load_all()

    def _load_all(self) -> None:
        for f in ACTIVE_DIR.glob("goal_*.yaml"):
            try:
                data = yaml.safe_load(f.read_text())
                g = GoalCard.model_validate(data)
                self._cache[g.id] = g
            except Exception as e:
                log.warning("Failed to load goal %s: %s", f, e)

    def save(self, goal: GoalCard) -> None:
        self._cache[goal.id] = goal
        path = ACTIVE_DIR / f"{goal.id}.yaml"
        path.write_text(yaml.dump(goal.model_dump(), sort_keys=False, allow_unicode=True))
        if goal.status in (GoalStatus.DONE, GoalStatus.CANCELLED):
            self._archive(goal, path)

    def _archive(self, goal: GoalCard, current_path: Path) -> None:
        year_month = goal.created_at[:7]  # YYYY-MM
        target = ARCHIVE_DIR / year_month / f"{goal.id}.yaml"
        target.parent.mkdir(parents=True, exist_ok=True)
        if current_path.exists():
            current_path.rename(target)

    def get(self, goal_id: str) -> GoalCard | None:
        return self._cache.get(goal_id)

    def list(self, status: GoalStatus | None = None) -> list[GoalCard]:
        if status is None:
            return list(self._cache.values())
        return [g for g in self._cache.values() if g.status == status]

    def delete(self, goal_id: str) -> None:
        self._cache.pop(goal_id, None)
        for path in (ACTIVE_DIR / f"{goal_id}.yaml",):
            if path.exists():
                path.unlink()
