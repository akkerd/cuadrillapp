# Punto de entrada único para personas, CI y Claude. `make` lista los comandos.
.DEFAULT_GOAL := help
SHELL := bash
SERVER := apps/server
PROTOCOL := packages/protocol
PLAYWRIGHT_DEPS ?=

help: ## Lista los comandos
	@grep -E '^[a-z0-9-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-10s %s\n", $$1, $$2}'

setup: ## Instala dependencias: Python (uv), Node (pnpm) y Chromium para e2e
	cd $(SERVER) && uv sync --frozen
	pnpm install --frozen-lockfile
	pnpm --filter e2e exec playwright install chromium $(PLAYWRIGHT_DEPS)

dev: ## Backend con recarga en :8000 + Vite en http://localhost:5173
	@trap 'kill 0' EXIT; \
	(cd $(SERVER) && uv run uvicorn cuadrillapp.main:create_app --factory --reload --port 8000) & \
	pnpm --filter web dev --host

gen: ## Regenera packages/protocol desde los modelos Pydantic
	cd $(SERVER) && uv run python -m cuadrillapp.protocol.export ../../$(PROTOCOL)
	pnpm --filter @cuadrillapp/protocol gen

gen-check: ## Falla si packages/protocol no está al día
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

build: ## Build de producción de la PWA
	pnpm --filter web build

e2e: build ## Playwright (móvil emulado) contra la build servida por Uvicorn
	pnpm --filter e2e test

verify: gen-check lint typecheck test e2e ## Todo lo que exige CI antes de mergear

.PHONY: help setup dev gen gen-check lint typecheck test build e2e verify
