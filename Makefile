.DEFAULT_GOAL := default

.PHONY: default install test lint upgrade build clean

default: install test

install:
	uv sync --all-extras

test:
	uv run pytest

lint:
	uv run ruff check src tests

upgrade:
	uv sync --upgrade --all-extras --dev

build:
	uv build

clean:
	-rm -rf dist/
	-rm -rf *.egg-info/
	-rm -rf .pytest_cache/
	-rm -rf .mypy_cache/
	-rm -rf .venv/
	-find . -type d -name "__pycache__" -exec rm -rf {} +
