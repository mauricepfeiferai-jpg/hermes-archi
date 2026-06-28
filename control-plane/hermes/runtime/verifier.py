"""Verifier — deterministic done-checks before a goal is marked done.

Supported check kinds (see /control-plane/hermes/verifier_rules.md):
  file_exists  file_matches  git_tag  git_clean  command_passes
  http_status  kg_node_exists  composite  (others marked TODO)
"""

from __future__ import annotations

import asyncio
import logging
import re
import subprocess
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.models import (  # noqa: E402
    GoalCard,
    VerifierCheck,
    VerifierResult,
    VerifierRun,
)

log = logging.getLogger("hermes.verifier")


class Verifier:
    def __init__(self, kg) -> None:
        self.kg = kg

    async def run(self, goal: GoalCard) -> VerifierRun:
        spec = goal.verifier or {}
        run = VerifierRun(goal_id=goal.id)
        checks = self._collect_checks(spec, goal)
        for chk in checks:
            res = await self._run_check(chk, goal)
            run.checks.append(res)
        passed = sum(1 for r in run.checks if r.result == "pass")
        failed = sum(1 for r in run.checks if r.result == "fail")
        if failed == 0 and passed > 0:
            run.overall = "pass"
        elif passed == 0:
            run.overall = "fail"
        else:
            run.overall = "partial"
        return run

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------

    def _collect_checks(self, spec: dict, goal: GoalCard) -> list[VerifierCheck]:
        """Flatten potentially composite spec into a list of VerifierCheck."""
        if not spec:
            return []
        if spec.get("type") == "composite" or spec.get("kind") == "composite":
            return [VerifierCheck(kind=c.get("kind"), args=c.get("args", c))
                    for c in spec.get("checks", [])]
        if "checks" in spec:
            return [VerifierCheck(kind=c.get("kind"), args=c.get("args", c))
                    for c in spec["checks"]]
        if "kind" in spec:
            return [VerifierCheck(kind=spec["kind"], args=spec.get("args", spec))]
        return []

    async def _run_check(self, chk: VerifierCheck, goal: GoalCard) -> VerifierResult:
        start = time.monotonic()
        try:
            handler = getattr(self, f"_chk_{chk.kind}", None)
            if not handler:
                return VerifierResult(check=chk, result="inconclusive",
                                      details=f"unknown check kind: {chk.kind}")
            res = await handler(chk.args, goal)
            return res
        finally:
            duration_ms = int((time.monotonic() - start) * 1000)
            log.info("Check %s: %sms", chk.kind, duration_ms)

    # ---------- Check implementations ----------

    async def _chk_file_exists(self, args, goal) -> VerifierResult:
        path = Path(self._resolve(args["path"], goal))
        ok = path.exists()
        return VerifierResult(check=VerifierCheck(kind="file_exists", args=args),
                              result="pass" if ok else "fail",
                              details=str(path))

    async def _chk_file_matches(self, args, goal) -> VerifierResult:
        path = Path(self._resolve(args["path"], goal))
        if not path.exists():
            return VerifierResult(check=VerifierCheck(kind="file_matches", args=args),
                                  result="fail", details=f"file missing: {path}")
        text = path.read_text(errors="replace")
        regex = args["regex"]
        flags = 0 if args.get("case_sensitive", False) else re.IGNORECASE
        ok = bool(re.search(regex, text, flags))
        return VerifierResult(check=VerifierCheck(kind="file_matches", args=args),
                              result="pass" if ok else "fail")

    async def _chk_git_tag(self, args, goal) -> VerifierResult:
        pattern = args["pattern"]
        proc = await asyncio.to_thread(subprocess.run,
                                       ["git", "tag", "--list", pattern],
                                       capture_output=True, text=True)
        ok = bool(proc.stdout.strip())
        return VerifierResult(check=VerifierCheck(kind="git_tag", args=args),
                              result="pass" if ok else "fail",
                              details=proc.stdout.strip()[:200])

    async def _chk_git_clean(self, args, goal) -> VerifierResult:
        proc = await asyncio.to_thread(subprocess.run,
                                       ["git", "status", "--porcelain"],
                                       capture_output=True, text=True)
        ok = proc.stdout.strip() == ""
        return VerifierResult(check=VerifierCheck(kind="git_clean", args=args),
                              result="pass" if ok else "fail",
                              details=proc.stdout.strip()[:200])

    async def _chk_command_passes(self, args, goal) -> VerifierResult:
        cmd = args["cmd"]
        cwd = args.get("cwd")
        expect_exit = args.get("expect_exit", 0)
        timeout = args.get("timeout_seconds", 300)
        try:
            proc = await asyncio.to_thread(
                subprocess.run, cmd, shell=True, cwd=cwd, capture_output=True,
                text=True, timeout=timeout,
            )
            ok = proc.returncode == expect_exit
            tail = (proc.stdout or proc.stderr or "")[-500:]
            return VerifierResult(check=VerifierCheck(kind="command_passes", args=args),
                                  result="pass" if ok else "fail",
                                  details=f"exit={proc.returncode} stdout_tail={tail}")
        except subprocess.TimeoutExpired:
            return VerifierResult(check=VerifierCheck(kind="command_passes", args=args),
                                  result="fail", details="timeout")

    async def _chk_http_status(self, args, goal) -> VerifierResult:
        url = args["url"]
        expect = args.get("expect", 200)
        timeout = args.get("timeout_seconds", 10)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.get(url, headers={"user-agent": "Hermes-Verifier/1.0"})
                ok = r.status_code == expect
                return VerifierResult(check=VerifierCheck(kind="http_status", args=args),
                                      result="pass" if ok else "fail",
                                      details=f"actual={r.status_code}")
        except Exception as e:
            return VerifierResult(check=VerifierCheck(kind="http_status", args=args),
                                  result="fail", details=str(e))

    async def _chk_kg_node_exists(self, args, goal) -> VerifierResult:
        label = args["label"]
        nodes = await self.kg.find_nodes(label=label, limit=500)
        wanted_props = args.get("props", {})
        for n in nodes:
            props = n["props"]
            if all(props.get(k) == v for k, v in wanted_props.items()):
                return VerifierResult(check=VerifierCheck(kind="kg_node_exists", args=args),
                                      result="pass", details=f"found node {n['id']}")
        return VerifierResult(check=VerifierCheck(kind="kg_node_exists", args=args),
                              result="fail", details="no matching node")

    async def _chk_human_signoff(self, args, goal) -> VerifierResult:
        # MVP: real signoff happens out-of-band via PATCH /goals/{id}.
        # For now we mark as inconclusive so the goal stays in `review`.
        return VerifierResult(check=VerifierCheck(kind="human_signoff", args=args),
                              result="inconclusive",
                              details="awaits human via PATCH /goals/{id}")

    # ---------- Utils ----------

    def _resolve(self, template: str, goal: GoalCard) -> str:
        """Replace {this.foo} placeholders with goal attributes."""
        out = template
        out = out.replace("{this.id}", goal.id)
        out = out.replace("{this.title}", goal.title)
        return out
