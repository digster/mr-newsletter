.PHONY: install run run-web run-web-debug build test test-e2e test-e2e-ci test-e2e-trace playwright-install lint format typecheck migrate check-env setup-gcloud kill help

help:
	@echo "Available commands:"
	@echo "  make install           - Install dependencies"
	@echo "  make setup-gcloud      - Interactive Google Cloud setup wizard"
	@echo "  make check-env         - Verify required environment variables"
	@echo "  make kill              - Kill any process using port 8550"
	@echo "  make run               - Run desktop app (auto-kills existing process)"
	@echo "  make run-web           - Run web app"
	@echo "  make run-web-debug     - Run web app for debugging with Claude"
	@echo "  make build             - Create standalone executable"
	@echo "  make test              - Run unit tests"
	@echo "  make test-e2e          - Run E2E tests with visible browser"
	@echo "  make test-e2e-ci       - Run E2E tests headless (for CI)"
	@echo "  make test-e2e-trace    - Run E2E tests with trace recording"
	@echo "  make playwright-install - Install Playwright browser binaries"
	@echo "  make lint              - Run linter"
	@echo "  make format            - Format code"
	@echo "  make typecheck         - Run type checker"
	@echo "  make migrate           - Run database migrations"

install:
	uv sync

check-env:
	@echo "Checking required environment variables..."
	@if [ -z "$$GOOGLE_CLIENT_ID" ]; then echo "ERROR: GOOGLE_CLIENT_ID is not set"; exit 1; fi
	@if [ -z "$$GOOGLE_CLIENT_SECRET" ]; then echo "ERROR: GOOGLE_CLIENT_SECRET is not set"; exit 1; fi
	@echo "All required environment variables are set."

setup-gcloud:
	uv run python scripts/setup_gcloud.py

kill:
	@echo "Killing any existing Flet processes on port 8550..."
	@lsof -ti :8550 | xargs kill -9 2>/dev/null || echo "No process to kill"

run: kill
	uv run python -m src.main

run-web:
	FLET_WEB_APP=true uv run python -m src.main

build:
	uv run flet pack src/main.py \
		--name "Mr Newsletter" \
		--add-data "src/config:src/config" \
		--add-data "src/ui:src/ui" \
		--hidden-import sqlalchemy \
		--hidden-import asyncpg \
		--hidden-import google.auth \
		--hidden-import apscheduler \
		--hidden-import aiosqlite \
		-y

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

run-web-debug:
	@echo "Starting Flet web app for debugging..."
	@echo "Use Claude's MCP browser tools to interact with http://127.0.0.1:8550"
	FLET_WEB_APP=true uv run python -m src.main

playwright-install:
	uv run playwright install chromium

test-e2e:
	uv run pytest tests/e2e/ -v --headed

test-e2e-ci:
	uv run pytest tests/e2e/ -v

test-e2e-trace:
	uv run pytest tests/e2e/ -v --tracing=on --output=tests/e2e/traces
