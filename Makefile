.DEFAULT_GOAL := help
BACKEND := backend

.PHONY: help install lint format typecheck test check run hooks

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install: ## Install backend dependencies and git hooks
	cd $(BACKEND) && uv sync
	cd $(BACKEND) && uv run pre-commit install

lint: ## Check lint rules and formatting
	cd $(BACKEND) && uv run ruff check . && uv run ruff format --check .

format: ## Auto-fix lint issues and format code
	cd $(BACKEND) && uv run ruff check --fix . && uv run ruff format .

typecheck: ## Run mypy static type checks
	cd $(BACKEND) && uv run mypy app

test: ## Run tests with coverage
	cd $(BACKEND) && uv run pytest --cov=app --cov-report=term-missing

check: lint typecheck test ## Run everything CI runs

run: ## Start the API with auto-reload
	cd $(BACKEND) && uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

hooks: ## Run all pre-commit hooks on every file
	cd $(BACKEND) && uv run pre-commit run --all-files
