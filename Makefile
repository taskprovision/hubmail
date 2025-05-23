.PHONY: help install dev stop restart status logs clean test backup restore check-api ui config-ui config-logs dashboard all-ui python-deps update-env

## Show this help
help:
	@echo '\nUsage: make [target]\n'
	@echo 'Available targets:'
	@echo '  install      Install project dependencies'
	@echo '  dev          Start all services in development mode'
	@echo '  stop         Stop all services'
	@echo '  restart      Restart all services'
	@echo '  status       Show services status'
	@echo '  logs         Show services logs (follow mode)'
	@echo '  app-logs     Show only the Python application logs'
	@echo '  config-logs  Show only the Configuration Dashboard logs'
	@echo '  ui           Open the Streamlit dashboard in browser'
	@echo '  config-ui    Open the Configuration Dashboard in browser'
	@echo '  dashboard    Start all services and open all dashboards'
	@echo '  all-ui       Open all UI dashboards in browser'
	@echo '  python-deps  Install Python dependencies locally (for development)'
	@echo '  update-env   Update .env file with new variables from .env.example'
	@echo '  clean        Clean up all containers, networks, and volumes'
	@echo '  test         Run tests'
	@echo '  check-api    Check the API health status'
	@echo '  backup       Create a backup of the current state'
	@echo '  restore      Restore from the latest backup'

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

## Show only the Python application logs
app-logs:
	docker-compose logs -f hubmail-app

## Show only the Configuration Dashboard logs
config-logs:
	docker-compose logs -f config-dashboard

## Open the Streamlit dashboard in browser
ui:
	@echo "Opening Streamlit dashboard in browser..."
	xdg-open http://localhost:${UI_PORT:-8501} 2>/dev/null || open http://localhost:${UI_PORT:-8501} 2>/dev/null || echo "Please open http://localhost:${UI_PORT:-8501} in your browser"

## Open the Configuration Dashboard in browser
config-ui:
	@echo "Opening Configuration Dashboard in browser..."
	xdg-open http://localhost:${CONFIG_DASHBOARD_PORT:-8502} 2>/dev/null || open http://localhost:${CONFIG_DASHBOARD_PORT:-8502} 2>/dev/null || echo "Please open http://localhost:${CONFIG_DASHBOARD_PORT:-8502} in your browser"

## Open all UI dashboards in browser
all-ui: ui config-ui
	@echo "Opening Grafana dashboard in browser..."
	xdg-open http://localhost:${GRAFANA_PORT:-3000} 2>/dev/null || open http://localhost:${GRAFANA_PORT:-3000} 2>/dev/null || echo "Please open http://localhost:${GRAFANA_PORT:-3000} in your browser"

## Start all services and open all dashboards
dashboard: dev
	@echo "Starting all services and opening dashboards..."
	@sleep 5
	@$(MAKE) all-ui

## Install Python dependencies locally (for development)
python-deps:
	@echo "Installing Python dependencies locally..."
	cd python_app && pip install -r requirements.txt

## Update .env file with new variables from .env.example
update-env:
	@echo "Updating .env file with new variables from .env.example..."
	@if [ ! -f .env ]; then \
		echo ".env file not found. Creating from .env.example..."; \
		cp .env.example .env; \
		echo ".env file created. Please edit it with your configuration."; \
	else \
		echo "Checking for new variables..."; \
		awk -F= '$$1 !~ /^[[:space:]]*#/ && $$1 !~ /^[[:space:]]*$$/ {print $$1}' .env.example > .env.example.vars; \
		awk -F= '$$1 !~ /^[[:space:]]*#/ && $$1 !~ /^[[:space:]]*$$/ {print $$1}' .env > .env.vars; \
		echo "New variables found:"; \
		for var in $$(grep -v -f .env.vars .env.example.vars); do \
			grep "^$$var=" .env.example >> .env; \
			echo "  - $$var"; \
		done; \
		rm -f .env.example.vars .env.vars; \
		echo "Update complete."; \
	fi

## Check the API health status
check-api:
	@echo "Checking API health..."
	curl -s http://localhost:${API_PORT:-3001}/health | jq .

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
