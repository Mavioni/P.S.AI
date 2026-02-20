.PHONY: install dev test lint run proto docker clean

# ── Setup ──────────────────────────────────────────────────────

install:
	cd backend && pip install .

dev:
	cd backend && pip install -e ".[dev,security]"

# ── Run ────────────────────────────────────────────────────────

run:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ── Test ───────────────────────────────────────────────────────

test:
	cd backend && python -m pytest tests/ -v

test-orchestrator:
	cd backend && python -m pytest tests/test_orchestrator/ -v

test-security:
	cd backend && python -m pytest tests/test_security/ -v

test-inference:
	cd backend && python -m pytest tests/test_inference/ -v

# ── Lint ───────────────────────────────────────────────────────

lint:
	cd backend && ruff check app/ tests/

format:
	cd backend && ruff format app/ tests/

# ── Proto ──────────────────────────────────────────────────────

proto:
	./scripts/generate_protos.sh

# ── Docker ─────────────────────────────────────────────────────

docker:
	docker compose up --build

docker-down:
	docker compose down

# ── Models ─────────────────────────────────────────────────────

setup-models:
	./scripts/setup_models.sh

# ── Clean ──────────────────────────────────────────────────────

clean:
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -f backend/data/psai.db
