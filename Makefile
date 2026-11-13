.PHONY: install lint format typecheck test check run docker

install:
	uv sync --all-extras

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

typecheck:
	uv run mypy

test:
	uv run pytest --cov

check: lint typecheck test

run:
	uv run uvicorn agent_engine.api.app:app --host 0.0.0.0 --port 8080

docker:
	docker build -t agentic-workflow-engine .
