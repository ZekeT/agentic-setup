.PHONY: setup fmt check test
setup:
	uv sync --extra dev
fmt:
	uv run ruff check --fix agentic_setup tests agentic
	uv run ruff format agentic_setup tests agentic
check:
	uv run ruff check agentic_setup tests agentic
	uv run ruff format --check agentic_setup tests agentic
	uv run mypy agentic_setup
	uv run pytest
test:
	uv run pytest
