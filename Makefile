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

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start all services (auto-detects GPU)
	@./scripts/start.sh up --build -d

down: ## Stop and remove all services
	@./scripts/start.sh down --remove-orphans

restart: ## Stop and restart all services
	@$(MAKE) down
	@$(MAKE) up

logs: ## Show logs. Ex: `make logs backend` for a specific service.
	@./scripts/start.sh logs $(ARGS)

test: ## Run all applicable test suites (Unit, Integration, Unity)
	@./scripts/run_all_tests.sh

test-unit: ## Run only the fast unit tests
	@./scripts/run_unit_tests.sh

test-integration: ## Run only the backend integration tests
	@./scripts/run_integration_tests.sh

test-unity: ## Run only the Unity tests (macOS/Windows only)
	@./scripts/run_unity_tests.sh
