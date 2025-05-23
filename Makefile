.PHONY: help install dev stop restart restart-config status logs app-logs config-logs debug-config ui config-ui dashboard all-ui python-deps update-env clean test python-tests python-docs generate-workflow-diagram backup restore check-api

## Show this help
help:
	@echo '\nUsage: make [target]\n'
	@echo 'Available targets:'
	@echo '  install      Install project dependencies'
	@echo '  dev          Start all services in development mode'
	@echo '  stop         Stop all services'
	@echo '  restart      Restart all services'
	@echo '  restart-config Restart only the Configuration Dashboard service'
	@echo '  status       Show services status'
	@echo '  logs         Show last 10 lines of logs for each running Docker container'
	@echo '  app-logs     Show only the Python application logs'
	@echo '  config-logs  Show only the Configuration Dashboard logs'
	@echo '  debug-config Debug the Configuration Dashboard service'
	@echo '  ui           Open the Streamlit dashboard in browser'
	@echo '  config-ui    Open the Configuration Dashboard in browser'
	@echo '  dashboard    Start all services and open all dashboards'
	@echo '  all-ui       Open all UI dashboards in browser'
	@echo '  python-deps  Install Python dependencies locally (for development)'
	@echo '  update-env   Update .env file with new variables from .env.example'
	@echo '  clean        Clean up all containers, networks, and volumes'
	@echo '  test         Run tests'
	@echo '  python-tests Run Python app tests'
	@echo '  python-docs  Generate Python app documentation'
	@echo '  generate-workflow-diagram Generate visual workflow diagrams'
	@echo '  check-api    Check the API health status'
	@echo '  backup       Create a backup of the current state'
	@echo '  restore      Restore from the latest backup'

## Install project dependencies
install: .env
	@echo -e "Installing project dependencies..."
	./install.sh

## Start all services
dev: .env
	@echo -e "Starting HubMail in development mode..."
	@echo -e "Access services at:"
	@echo -e "- Node-RED: http://localhost:1880"
	@echo -e "- Grafana: http://localhost:3000 (admin/admin)"
	@echo -e "- Prometheus: http://localhost:9090"
	docker-compose up -d

## Stop all services
stop:
	@echo -e "Stopping all services..."
	docker-compose down

## Restart all services
restart: stop dev

## Show services status
status:
	@echo -e "Services status:"
	docker-compose ps

## Show last 10 lines of logs for each Docker container
logs:
	@echo -e "Showing last 10 lines of logs for each running Docker container..."
	clear
	@for c in $$(docker ps --format '{{.Names}}'); do \
	  echo -e "\docker logs $$c"; \
	  docker logs --tail 15 $$c 2>&1; \
	done

## Show only the Python application logs
app-logs:
	docker-compose logs -f hubmail-app

## Show only the Configuration Dashboard logs
config-logs:
	docker-compose logs -f config-dashboard

## Restart only the Configuration Dashboard service
restart-config:
	@echo -e "Restarting Configuration Dashboard..."
	docker-compose restart config-dashboard
	@echo -e "Configuration Dashboard restarted. Access it at http://localhost:${CONFIG_DASHBOARD_PORT:-8502}"

## Debug the Configuration Dashboard service
debug-config:
	@echo -e "Debugging Configuration Dashboard..."
	@echo -e "Checking if files are accessible inside the container..."
	docker-compose exec config-dashboard ls -la /app
	@echo -e "\nChecking if .env file is accessible..."
	docker-compose exec config-dashboard ls -la /app/.env || echo -e "File not found"
	@echo -e "\nChecking if docker-compose.yml file is accessible..."
	docker-compose exec config-dashboard ls -la /app/docker-compose.yml || echo -e "File not found"

## Open the Streamlit dashboard in browser
ui:
	@echo -e "Opening Streamlit dashboard in browser..."
	xdg-open http://localhost:${UI_PORT:-8501} 2>/dev/null || open http://localhost:${UI_PORT:-8501} 2>/dev/null || echo -e "Please open http://localhost:${UI_PORT:-8501} in your browser"

## Open the Configuration Dashboard in browser
config-ui:
	@echo -e "Opening Configuration Dashboard in browser..."
	xdg-open http://localhost:${CONFIG_DASHBOARD_PORT:-8502} 2>/dev/null || open http://localhost:${CONFIG_DASHBOARD_PORT:-8502} 2>/dev/null || echo -e "Please open http://localhost:${CONFIG_DASHBOARD_PORT:-8502} in your browser"

## Open all UI dashboards in browser
all-ui: ui config-ui
	@echo -e "Opening Grafana dashboard in browser..."
	xdg-open http://localhost:${GRAFANA_PORT:-3000} 2>/dev/null || open http://localhost:${GRAFANA_PORT:-3000} 2>/dev/null || echo -e "Please open http://localhost:${GRAFANA_PORT:-3000} in your browser"

## Start all services and open all dashboards
dashboard: dev
	@echo -e "Starting all services and opening dashboards..."
	@sleep 5
	@$(MAKE) all-ui

## Install Python dependencies locally (for development)
python-deps:
	@echo -e "Installing Python dependencies locally..."
	cd python_app && pip install -r requirements.txt

## Update .env file with new variables from .env.example
update-env:
	@echo -e "Updating .env file with new variables from .env.example..."
	@if [ ! -f .env ]; then \
		echo -e ".env file not found. Creating from .env.example..."; \
		cp .env.example .env; \
		echo -e ".env file created. Please edit it with your configuration."; \
	else \
		echo -e "Checking for new variables..."; \
		awk -F= '$$1 !~ /^[[:space:]]*#/ && $$1 !~ /^[[:space:]]*$$/ {print $$1}' .env.example > .env.example.vars; \
		awk -F= '$$1 !~ /^[[:space:]]*#/ && $$1 !~ /^[[:space:]]*$$/ {print $$1}' .env > .env.vars; \
		echo -e "New variables found:"; \
		for var in $$(grep -v -f .env.vars .env.example.vars); do \
			grep "^$$var=" .env.example >> .env; \
			echo -e "  - $$var"; \
		done; \
		rm -f .env.example.vars .env.vars; \
		echo -e "Update complete."; \
	fi

## Check the API health status
check-api:
	@echo -e "Checking API health..."
	curl -s http://localhost:${API_PORT:-3001}/health | jq .

## Clean up all containers, networks, and volumes
clean:
	@echo -e "Cleaning up..."
	docker-compose down -v --remove-orphans
	@echo -e "Clean complete!"

## Run tests
test:
	@echo -e "Running tests..."
	./scripts/test-flow.sh

## Run Python app tests
python-tests:
	@echo -e "Running Python app tests..."
	cd python_app && python -m tests.run_tests

## Generate Python app documentation
python-docs:
	@echo -e "Generating Python app documentation..."
	@echo -e "Documentation available at python_app/docs/README.md"
	@if [ ! -d python_app/docs ]; then \
		mkdir -p python_app/docs; \
	fi

## Generate visual workflow diagrams
generate-workflow-diagram:
	@echo -e "Generating workflow diagrams..."
	@if ! pip list | grep -q graphviz; then \
		echo -e "Installing graphviz Python package..."; \
		pip install graphviz; \
	fi
	@if ! command -v dot >/dev/null 2>&1; then \
		echo -e "Graphviz not found. Please install it:"; \
		echo -e "  Ubuntu/Debian: sudo apt-get install graphviz"; \
		echo -e "  CentOS/RHEL: sudo yum install graphviz"; \
		echo -e "  macOS: brew install graphviz"; \
		exit 1; \
	fi
	cd python_app && python docs/workflow_diagram.py
	@echo -e "Workflow diagrams generated in python_app/docs/"

## Create a backup
backup:
	@echo -e "Creating backup..."
	./scripts/backup.sh

## Restore from backup
restore:
	@echo -e "WARNING: This will overwrite current data. Continue? [y/N] "
	@read -p "" confirm && [ $$confirm = y ] || [ $$confirm = Y ] || (echo -e "Restore cancelled"; exit 1)
	@echo -e "Restoring from backup..."
	# Add restore command here

## Setup environment file if it doesn't exist
.env:
	@if [ ! -f .env ]; then \
		echo -e ".env file not found. Creating from .env.example..."; \
		cp .env.example .env; \
		echo -e ".env file created. Please edit it with your configuration."; \
	fi

## Show help by default
.DEFAULT_GOAL := help
