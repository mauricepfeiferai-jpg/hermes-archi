# Beispiel: LLM Tracer + Ollama Cloud

```python
from ollama_cloud_client import call_ollama_cloud
from llm_tracer import trace_llm_call

def make_call():
    return call_ollama_cloud(
        "Return a JSON object with key 'hello'.",
        model="deepseek-v4-flash:cloud",
        timeout=60,
    )

result = trace_llm_call(
    model="deepseek-v4-flash:cloud",
    messages=[{"role": "user", "content": "Return a JSON object with key 'hello'."}],
    make_call=make_call,
    workflow="example_workflow",
    agent="Hermes",
    metadata={"source": "example"},
)
```
