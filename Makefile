.PHONY: help install start stop restart status logs clean test backup restore

# Colors
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

## Show this help
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/(^[a-zA-Z\-\_0-9]+:.*?##.*$$)|(^##)/ { \
		htps://www.gnu.org/software/make/manual/html_node/Special-Variables.html#Special-Variables
		if ($$1 ~ /^[a-z\-]+:.*?##.*$$/) { \
			printf "  ${YELLOW}%-20s${GREEN}%s${RESET}\n", $$1, $$2 \
		} else if ($$1 ~ /^## .*$$/) { \
			printf "${YELLOW}%s${RESET}\n", substr($$1,4) \
		} \
	}' $(MAKEFILE_LIST)

## Install project dependencies
install: .env ## Install project dependencies
	@echo "${GREEN}🚀 Installing project dependencies...${RESET}"
	./install.sh

## Start all services
dev: .env ## Start all services in development mode
	@echo "${GREEN}🚀 Starting HubMail in development mode...${RESET}
${YELLOW}Access services at:${RESET}
- Node-RED: http://localhost:1880\n- Grafana: http://localhost:3000 (admin/admin)\n- Prometheus: http://localhost:9090${RESET}"
	docker-compose up -d

## Stop all services
stop: ## Stop all services
	@echo "${YELLOW}🛑 Stopping all services...${RESET}"
	docker-compose down

## Restart all services
restart: stop dev ## Restart all services

## Show services status
status: ## Show services status
	@echo "${GREEN}📊 Services status:${RESET}"
	docker-compose ps

## Show services logs
logs: ## Show services logs (follow mode)
	docker-compose logs -f

## Clean up all containers, networks, and volumes
clean: ## Clean up all containers, networks, and volumes
	@echo "${YELLOW}🧹 Cleaning up...${RESET}"
	docker-compose down -v --remove-orphans
	@echo "${GREEN}✅ Clean complete!${RESET}"

## Run tests
test: ## Run tests
	@echo "${GREEN}🧪 Running tests...${RESET}"
	./scripts/test-flow.sh

## Create a backup
backup: ## Create a backup of the current state
	@echo "${GREEN}💾 Creating backup...${RESET}"
	./scripts/backup.sh

## Restore from backup
restore: ## Restore from the latest backup
	@echo "${YELLOW}⚠️  WARNING: This will overwrite current data. Continue? [y/N] ${RESET}"
	@read -p "" confirm && [ $$confirm = y ] || [ $$confirm = Y ] || (echo "${YELLOW}Restore cancelled${RESET}"; exit 1)
	@echo "${GREEN}🔄 Restoring from backup...${RESET}"
	# Add restore command here

## Setup environment file if it doesn't exist
.env:
	@if [ ! -f .env ]; then \
		echo "${YELLOW}⚠️  .env file not found. Creating from .env.example...${RESET}"; \
		cp .env.example .env; \
		echo "${GREEN}✅ .env file created. Please edit it with your configuration.${RESET}"; \
	fi

## Show help by default
.DEFAULT_GOAL := help
