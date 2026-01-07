.PHONY: install run run-web build test lint format typecheck migrate help

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Run desktop app"
	@echo "  make run-web    - Run web app"
	@echo "  make build      - Create standalone executable"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linter"
	@echo "  make format     - Format code"
	@echo "  make typecheck  - Run type checker"
	@echo "  make migrate    - Run database migrations"

install:
	uv sync

run:
	uv run python -m src.main

run-web:
	FLET_WEB_APP=true uv run python -m src.main

build:
	uv run flet pack src/main.py \
		--name "Newsletter Manager" \
		--add-data "src/config:src/config" \
		--add-data "src/ui:src/ui" \
		--hidden-import sqlalchemy \
		--hidden-import asyncpg \
		--hidden-import google.auth \
		--hidden-import apscheduler

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy src/

migrate:
	uv run alembic upgrade head
