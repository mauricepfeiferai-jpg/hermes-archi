#!/usr/bin/env python3
"""Ollama Cloud client wrapper for Hermes/Hecate via local Ollama HTTP API.

Replaces direct Kimi API calls with Ollama Cloud models:
- deepseek-v4-flash:cloud  (fast, default for simple tasks)
- glm-5.2:cloud            (strong reasoning, default for complex tasks)
- kimi-k2.7-code:cloud     (legacy alias)

Uses http://localhost:11434/api/generate for clean JSON/text output.
"""
import json, re, requests
from typing import Optional

OLLAMA_HOST = "http://localhost:11434"

# Default model routing
DEFAULT_FAST = "deepseek-v4-flash:cloud"
DEFAULT_REASONING = "glm-5.2:cloud"


def call_ollama_cloud(
    prompt: str,
    model: str = DEFAULT_FAST,
    temperature: float = 0.0,
    timeout: int = 120,
    stream: bool = False,
) -> dict:
    """Call Ollama Cloud via local Ollama API and return structured result."""
    try:
        url = f"{OLLAMA_HOST}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {"temperature": temperature},
        }
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        return {
            "raw": data.get("response", ""),
            "model": model,
            "done": data.get("done", False),
            "total_duration_ms": data.get("total_duration", 0) / 1_000_000,
            "load_duration_ms": data.get("load_duration", 0) / 1_000_000,
            "prompt_eval_count": data.get("prompt_eval_count", 0),
            "eval_count": data.get("eval_count", 0),
            "error": None,
        }
    except requests.exceptions.Timeout:
        return {"raw": "", "model": model, "error": "timeout"}
    except Exception as e:
        return {"raw": "", "model": model, "error": str(e)}


def extract_json_array(text: str) -> list:
    """Find and parse the last complete JSON array in text."""
    starts = [i for i, ch in enumerate(text) if ch == "["]
    for start in reversed(starts):
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break
    return []


def extract_json_object(text: str) -> dict:
    """Find and parse the last complete JSON object in text."""
    matches = list(re.finditer(r"\{.*?\}", text, re.DOTALL))
    for m in reversed(matches):
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            continue
    return {}


def generate_text(prompt: str, model: str = DEFAULT_FAST, timeout: int = 120) -> str:
    """Simple text generation. Returns raw response."""
    result = call_ollama_cloud(prompt, model=model, timeout=timeout)
    return result.get("raw", "")


def generate_json_array(
    prompt: str, model: str = DEFAULT_FAST, timeout: int = 120
) -> list:
    """Generate and parse a JSON array."""
    text = generate_text(prompt, model=model, timeout=timeout)
    return extract_json_array(text)


def generate_json_object(
    prompt: str, model: str = DEFAULT_FAST, timeout: int = 120
) -> dict:
    """Generate and parse a JSON object."""
    text = generate_text(prompt, model=model, timeout=timeout)
    return extract_json_object(text)


if __name__ == "__main__":
    import sys

    model = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FAST
    prompt = (
        " ".join(sys.argv[2:])
        if len(sys.argv) > 2
        else "Return a JSON object with key 'hello'."
    )

    print(f"Testing Ollama Cloud: {model}")
    result = call_ollama_cloud(prompt, model=model)
    print("RAW:")
    print(result["raw"][:500])
    print("---")
    print("JSON object:", generate_json_object(prompt, model=model))
    print("JSON array:", generate_json_array("Return [1,2,3]", model=model))
