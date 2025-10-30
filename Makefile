# This captures all command-line arguments except for the target name.
# It allows passing arguments to the underlying commands.
# Example: `make logs backend` will pass `backend` to the logs command.
ARGS = $(filter-out $@,$(MAKECMDGOALS))

# By default, running 'make' will show the help message.
.DEFAULT_GOAL := help

# Self-documenting commands:
# The `##` comments will be automatically displayed by the `help` command.
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help up down restart logs test test-unit test-integration test-unity

up: ## Start all services (auto-detects GPU).
	@./scripts/start.sh up --build -d

down: ## Stop and remove all services.
	@./scripts/start.sh down --remove-orphans

restart: down up ## Stop and restart all services. Alias for `down` + `up`.

logs: ## Show logs. Ex: `make logs <service name>` for a specific service.
	@./scripts/start.sh logs $(ARGS)

unity-editor: ## Open the Unity project in the editor (macOS/Windows only).
	@./scripts/open_unity_editor.sh

open-unity: unity-editor ## Alias of `unity-editor`.

test: ## Run all applicable test suites (Unit, Integration, Unity).
	@./scripts/run_all_tests.sh

test-unit: ## Run unit tests.
	@./scripts/run_unit_tests.sh

test-integration: ## Run backend integration tests.
	@./scripts/run_integration_tests.sh

test-unity: ## Run Unity tests (macOS/Windows only).
	@./scripts/run_unity_tests.sh

validate: format lint ## Validate code. Alias for `format` + `lint`.

format: ## Format all source code with Black, Ruff Formatter, and Prettier.
	@./scripts/format.sh

lint: ## Lint all source code with Ruff and ESLint.
	@./scripts/lint.sh

clean: ## Remove temp files, caches, build artifacts, and legacy SDKs.
	@./scripts/clean.sh

help: ## Show this help message.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
