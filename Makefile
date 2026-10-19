.PHONY: setup fmt check test
setup:
	uv sync --extra dev
fmt:
	uv run ruff check --fix starter tests engineering
	uv run ruff format starter tests engineering
check:
	uv run ruff check starter tests engineering
	uv run ruff format --check starter tests engineering
	uv run mypy starter
	uv run pytest
test:
	uv run pytest
