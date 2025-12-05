# -----------------------------------------------
# Catch-all rule — ignore extra args like `backend`
# -----------------------------------------------
%:
	@:

# -----------------------------------------------
# Variables
# -----------------------------------------------

# This captures all command-line arguments except for the target name.
# It allows passing arguments to the underlying commands.
# Example: `make logs backend` will pass `backend` to the logs command.
ARGS = $(filter-out $@,$(MAKECMDGOALS))

# -----------------------------------------------
# Targets
# -----------------------------------------------

# By default, running 'make' will show the help message.
.DEFAULT_GOAL := help

# Self-documenting commands:
# The `##` comments will be automatically displayed by the `help` command.
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help up down restart logs test test-unit test-integration test-unity coverage-report

up: ## Start all services (auto-detects GPU).
	@./scripts/docker-compose-manager.sh up --build -d

down: ## Stop and remove all services.
	@./scripts/docker-compose-manager.sh down --remove-orphans

restart: ## Restart all services.
	@./scripts/docker-compose-manager.sh restart

rebuild: ## Rebuild specific service(s) or all if none provided. Ex: `make rebuild <service name>`.
	@echo "Rebuilding service(s): $(ARGS)"
	@./scripts/docker-compose-manager.sh down $(ARGS)
	@./scripts/docker-compose-manager.sh up --build -d $(ARGS)

logs: ## Show logs. Ex: `make logs <service name>` for a specific service.
	@./scripts/docker-compose-manager.sh logs $(ARGS)

open-unity: ## Open the Unity project in the editor (macOS/Windows only).
	@./scripts/open_unity_editor.sh

test: ## Run all applicable test suites (Unit, Integration, Unity).
	@./scripts/run_all_tests.sh

test-unit: ## Run unit tests.
	@./scripts/run_unit_tests.sh

test-integration: ## Run backend integration tests.
	@./scripts/run_integration_tests.sh

test-unity: ## Run Unity tests (macOS/Windows only).
	@./scripts/run_unity_tests.sh

coverage-report: ## Generate and open test coverage report by installing all dependencies and running tests locally
	@./scripts/generate_coverage.sh

validate: format lint ## Validate code. Alias for `format` + `lint`.

format: ## Format all source code with Black, Ruff Formatter, and Prettier.
	@./scripts/format.sh

lint: ## Lint all source code with Ruff and ESLint.
	@./scripts/lint.sh

clean: ## Clean up temporary Python and Node files.
	@./scripts/clean.sh --python --node

clean-deep: ## Clean up ALL temporary files, including Unity and Docker.
	@./scripts/clean.sh --deep

help: ## Show this help message.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
