# Single entry point for people, CI and Claude. Run `make` to list the commands.
.DEFAULT_GOAL := help
SHELL := bash
SERVER := apps/server
PROTOCOL := packages/protocol
PLAYWRIGHT_DEPS ?=

help: ## List the commands
	@grep -E '^[a-z0-9-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-10s %s\n", $$1, $$2}'

setup: ## Install dependencies: Python (uv), Node (pnpm) and Chromium for e2e
	cd $(SERVER) && uv sync --frozen
	pnpm install --frozen-lockfile
	pnpm --filter e2e exec playwright install chromium $(PLAYWRIGHT_DEPS)

dev: ## Backend with reload on :8000 + Vite on http://localhost:5173
	@trap 'kill 0' EXIT; \
	(cd $(SERVER) && uv run uvicorn cuadrillapp.main:create_app --factory --reload --port 8000) & \
	pnpm --filter web dev --host

gen: ## Regenerate packages/protocol from the Pydantic models
	cd $(SERVER) && uv run python -m cuadrillapp.protocol.export ../../$(PROTOCOL)
	pnpm --filter @cuadrillapp/protocol gen

gen-check: ## Fail if packages/protocol is out of date
	./scripts/gen-check.sh

lint: ## Ruff + Biome
	cd $(SERVER) && uv run ruff check . && uv run ruff format --check .
	pnpm exec biome ci .

typecheck: ## mypy (strict) + tsc
	cd $(SERVER) && uv run mypy
	pnpm -r typecheck

test: ## pytest + Vitest
	cd $(SERVER) && uv run pytest
	pnpm --filter web test

build: ## Production build of the PWA
	pnpm --filter web build

e2e: build ## Playwright (emulated phone) against the build served by Uvicorn
	pnpm --filter e2e test

verify: gen-check lint typecheck test e2e ## Everything CI requires before merging

.PHONY: help setup dev gen gen-check lint typecheck test build e2e verify
