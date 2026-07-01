#!/usr/bin/env python3
"""LLM observability: trace every LLM call with tokens, latency, cost, errors.
Usage: wrap any LLM client call with trace_llm_call().
"""
import json, time, os, uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Any, Callable

REPO = Path.home() / "ai-empire" / "projects" / "hermes-archi"
LOG_DIR = REPO / "00_SYSTEM" / "logs"
LOG_FILE = LOG_DIR / "llm_traces.jsonl"

# Cost per 1M tokens (input + output blended approximations, update as needed)
COST_PER_1M = {
    "claude-sonnet-4": 3.00 + 15.00,
    "claude-sonnet": 3.00 + 15.00,
    "claude-opus": 15.00 + 75.00,
    "kimi-k2.6": 0.50 + 2.00,
    "kimi": 0.50 + 2.00,
    "gpt-4o": 5.00 + 15.00,
    "ollama": 0.00,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    rate = COST_PER_1M.get(model.lower(), 2.00)
    return ((input_tokens + output_tokens) / 1_000_000) * rate


def trace_llm_call(
    model: str,
    messages: list,
    make_call: Callable[[], Any],
    workflow: str = "unknown",
    agent: str = "Hermes",
    metadata: Optional[dict] = None,
):
    """Wrap an LLM call with tracing. Returns the call result."""
    trace_id = f"T_{_now().replace(':', '-')}_{uuid.uuid4().hex[:8]}"
    start = time.time()
    error = None
    result = None
    input_tokens = 0
    output_tokens = 0

    for m in messages:
        text = m.get("content") or ""
        if isinstance(text, str):
            input_tokens += max(1, len(text) // 4)
        elif isinstance(text, list):
            for part in text:
                if isinstance(part, dict) and "text" in part:
                    input_tokens += max(1, len(part["text"]) // 4)

    try:
        result = make_call()
        if isinstance(result, dict):
            usage = result.get("usage", {})
            input_tokens = usage.get("input_tokens", input_tokens)
            output_tokens = usage.get("output_tokens", output_tokens)
            if "completion" in result and isinstance(result["completion"], str):
                output_tokens = max(output_tokens, len(result["completion"]) // 4)
        elif hasattr(result, "usage"):
            usage = result.usage
            input_tokens = getattr(usage, "input_tokens", input_tokens)
            output_tokens = getattr(usage, "output_tokens", output_tokens)
    except Exception as e:
        error = str(e)

    latency_ms = int((time.time() - start) * 1000)
    cost = estimate_cost(model, input_tokens, output_tokens)

    trace = {
        "trace_id": trace_id,
        "ts": _now(),
        "agent": agent,
        "workflow": workflow,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_ms": latency_ms,
        "cost_usd": round(cost, 6),
        "error": error,
        "metadata": metadata or {},
    }

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(trace, ensure_ascii=False) + "\n")

    if error:
        raise RuntimeError(error)

    return result


def tail_traces(limit: int = 10) -> list:
    if not LOG_FILE.exists():
        return []
    lines = LOG_FILE.read_text().splitlines()
    return [json.loads(line) for line in lines[-limit:]]


def cost_by_workflow() -> dict:
    costs = {}
    for trace in tail_traces(10000):
        wf = trace.get("workflow", "unknown")
        costs[wf] = costs.get(wf, 0.0) + trace.get("cost_usd", 0.0)
    return {k: round(v, 6) for k, v in sorted(costs.items(), key=lambda x: -x[1])}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tail", type=int, default=10)
    parser.add_argument("--cost-by-workflow", action="store_true")
    args = parser.parse_args()

    if args.cost_by_workflow:
        print(json.dumps(cost_by_workflow(), indent=2, ensure_ascii=False))
    else:
        for t in tail_traces(args.tail):
            print(json.dumps(t, indent=2, ensure_ascii=False))
