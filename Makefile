.PHONY: install install-python install-ts typecheck syntax-check test help

help:
	@echo "hermes-archi — Unified Agent Control Plane"
	@echo ""
	@echo "  make install        Install all dependencies (Python + TS)"
	@echo "  make install-python Install Python deps for control-plane + trading"
	@echo "  make install-ts     Install TypeScript deps for model-layer + telegram"
	@echo "  make syntax-check   Run Python syntax check on all .py files"
	@echo "  make typecheck      Run TypeScript type check on all .ts files"
	@echo "  make test           Run Python test suite"

install: install-python install-ts

install-python:
	@echo "→ Setting up Python venv at .venv/ ..."
	@python3 -m venv .venv
	@echo "→ Installing control-plane Python deps..."
	.venv/bin/pip install -r control-plane/requirements.txt
	@echo "→ Installing trading Python deps..."
	.venv/bin/pip install -r trading/requirements.txt
	@echo "✓ Python deps installed. Activate with: source .venv/bin/activate"

install-ts:
	@echo "→ Installing model-layer TS deps..."
	cd model-layer && npm install
	@echo "→ Installing telegram integration TS deps..."
	cd integrations/telegram && npm install

syntax-check:
	@echo "→ Python syntax check..."
	@find . -name "*.py" -not -path "./_archived*" | xargs -I{} python3 -m py_compile {} && echo "✓ All Python files OK"

typecheck:
	@echo "→ TypeScript type check (model-layer)..."
	cd model-layer && npm run typecheck
	@echo "→ TypeScript type check (telegram)..."
	cd integrations/telegram && npm run typecheck

test:
	@echo "→ Running control-plane tests..."
	cd control-plane && python -m pytest tests/ -v
