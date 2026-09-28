.DEFAULT_GOAL := help
BACKEND := backend
ML := ml

.PHONY: help install format check hooks
.PHONY: lint typecheck test run
.PHONY: ml-lint ml-typecheck ml-test ml-check
.PHONY: up deps down reset logs ps test-integration

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-17s\033[0m %s\n", $$1, $$2}'

# ---------- Everyday ----------
install: ## Install backend and ml dependencies, and git hooks
	cd $(BACKEND) && uv sync
	cd $(ML) && uv sync
	cd $(BACKEND) && uv run pre-commit install

format: ## Auto-fix lint issues and format code (backend and ml)
	cd $(BACKEND) && uv run ruff check --fix . && uv run ruff format .
	cd $(ML) && uv run ruff check --fix . && uv run ruff format .

check: lint typecheck test ml-check ## Run every non-Docker check CI runs

hooks: ## Run all pre-commit hooks on every file
	cd $(BACKEND) && uv run pre-commit run --all-files

# ---------- Backend ----------
lint: ## Backend: check lint rules and formatting
	cd $(BACKEND) && uv run ruff check . && uv run ruff format --check .

typecheck: ## Backend: run mypy static type checks
	cd $(BACKEND) && uv run mypy app

test: ## Backend: run unit tests with coverage
	cd $(BACKEND) && uv run pytest --cov=app --cov-report=term-missing

run: ## Backend: start the API locally with auto-reload (use `make deps` first)
	cd $(BACKEND) && uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# ---------- ML ----------
ml-lint: ## ML: check lint rules and formatting
	cd $(ML) && uv run ruff check . && uv run ruff format --check .

ml-typecheck: ## ML: run mypy static type checks
	cd $(ML) && uv run mypy src

ml-test: ## ML: run tests with coverage
	cd $(ML) && uv run pytest --cov=radassist_ml --cov-report=term-missing

ml-check: ml-lint ml-typecheck ml-test ## ML: run everything the ml CI job runs

# ---------- Docker ----------
up: ## Build and start the full stack (API + dependencies)
	docker compose up --build --detach --wait

deps: ## Start only db, redis and storage (for `make run`)
	docker compose up --detach --wait db redis storage

down: ## Stop all containers (data is kept)
	docker compose down

reset: ## Stop all containers and DELETE all local data
	docker compose down --volumes

logs: ## Follow the logs of all containers
	docker compose logs --follow

ps: ## Show container status and health
	docker compose ps

test-integration: ## Run integration tests (needs `make up` or `make deps`)
	cd $(BACKEND) && uv run pytest -m integration
