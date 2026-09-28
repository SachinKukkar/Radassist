.DEFAULT_GOAL := help
BACKEND := backend

.PHONY: help install lint format typecheck test check run hooks
.PHONY: up deps down reset logs ps test-integration

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-17s\033[0m %s\n", $$1, $$2}'

# ---------- Local development (no Docker needed) ----------
install: ## Install backend dependencies and git hooks
	cd $(BACKEND) && uv sync
	cd $(BACKEND) && uv run pre-commit install

lint: ## Check lint rules and formatting
	cd $(BACKEND) && uv run ruff check . && uv run ruff format --check .

format: ## Auto-fix lint issues and format code
	cd $(BACKEND) && uv run ruff check --fix . && uv run ruff format .

typecheck: ## Run mypy static type checks
	cd $(BACKEND) && uv run mypy app

test: ## Run unit tests with coverage
	cd $(BACKEND) && uv run pytest --cov=app --cov-report=term-missing

check: lint typecheck test ## Run everything the backend CI job runs

run: ## Start the API on your laptop with auto-reload (use `make deps` first)
	cd $(BACKEND) && uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

hooks: ## Run all pre-commit hooks on every file
	cd $(BACKEND) && uv run pre-commit run --all-files

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
