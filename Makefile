.PHONY: help install dev stop restart status logs clean test backup restore

## Show this help
help:
	@echo '\nUsage: make [target]\n'
	@echo 'Available targets:'
	@echo '  install    Install project dependencies'
	@echo '  dev        Start all services in development mode'
	@echo '  stop       Stop all services'
	@echo '  restart    Restart all services'
	@echo '  status     Show services status'
	@echo '  logs       Show services logs (follow mode)'
	@echo '  clean      Clean up all containers, networks, and volumes'
	@echo '  test       Run tests'
	@echo '  backup     Create a backup of the current state'
	@echo '  restore    Restore from the latest backup'

## Install project dependencies
install: .env
	@echo "Installing project dependencies..."
	./install.sh

## Start all services
dev: .env
	@echo "Starting HubMail in development mode..."
	@echo "Access services at:"
	@echo "- Node-RED: http://localhost:1880"
	@echo "- Grafana: http://localhost:3000 (admin/admin)"
	@echo "- Prometheus: http://localhost:9090"
	docker-compose up -d

## Stop all services
stop:
	@echo "Stopping all services..."
	docker-compose down

## Restart all services
restart: stop dev

## Show services status
status:
	@echo "Services status:"
	docker-compose ps

## Show services logs
logs:
	docker-compose logs -f

## Clean up all containers, networks, and volumes
clean:
	@echo "Cleaning up..."
	docker-compose down -v --remove-orphans
	@echo "Clean complete!"

## Run tests
test:
	@echo "Running tests..."
	./scripts/test-flow.sh

## Create a backup
backup:
	@echo "Creating backup..."
	./scripts/backup.sh

## Restore from backup
restore:
	@echo "WARNING: This will overwrite current data. Continue? [y/N] "
	@read -p "" confirm && [ $$confirm = y ] || [ $$confirm = Y ] || (echo "Restore cancelled"; exit 1)
	@echo "Restoring from backup..."
	# Add restore command here

## Setup environment file if it doesn't exist
.env:
	@if [ ! -f .env ]; then \
		echo ".env file not found. Creating from .env.example..."; \
		cp .env.example .env; \
		echo ".env file created. Please edit it with your configuration."; \
	fi

## Show help by default
.DEFAULT_GOAL := help
