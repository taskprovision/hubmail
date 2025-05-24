# Makefile for testing all Taskinity examples
# This file provides commands to test all examples in the project

# Variables
PYTHON = python3
DOCKER_COMPOSE = docker-compose

# Taskinity module paths
TASKINITY_CORE = ../taskinity/core
TASKINITY_EXTENSIONS = ../taskinity/extensions
TASKINITY_UTILS = ../taskinity/utils

# Add Taskinity modules to PYTHONPATH
EXPORT_PYTHONPATH = export PYTHONPATH=$(shell pwd)/..:$(PYTHONPATH)

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make test-all              - Run all tests for all examples"
	@echo "  make run-all               - Run all examples"
	@echo "  make docker-up-all         - Start all Docker environments"
	@echo "  make docker-down-all       - Stop all Docker environments"
	@echo ""
	@echo "Email Processing Examples:"
	@echo "  make email-test            - Run email processing tests"
	@echo "  make email-run             - Run email processing example"
	@echo "  make email-docker-basic    - Start basic email Docker environment"
	@echo "  make email-docker-mock     - Start mock email Docker environment"
	@echo "  make email-docker-full     - Start full email Docker environment"
	@echo "  make email-docker-down     - Stop all email Docker environments"
	@echo ""
	@echo "Data Processing Examples:"
	@echo "  make data-test             - Run data processing tests"
	@echo "  make data-run              - Run data processing example"
	@echo ""
	@echo "API Integration Examples:"
	@echo "  make api-test              - Run API integration tests"
	@echo "  make api-run               - Run API integration example"
	@echo ""
	@echo "Parallel Tasks Examples:"
	@echo "  make parallel-test         - Run parallel tasks tests"
	@echo "  make parallel-run          - Run parallel tasks example"
	@echo ""
	@echo "Visualization Examples:"
	@echo "  make viz-test              - Run visualization tests"
	@echo "  make viz-run               - Run visualization example"
	@echo ""
	@echo "Performance Benchmarks:"
	@echo "  make perf-test             - Run performance benchmark tests"
	@echo "  make perf-run              - Run performance benchmarks"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean                 - Clean up temporary files"
	@echo "  make update-viz            - Update DSL visualizer in all Markdown files"

# Run all tests
.PHONY: test-all
test-all: email-test data-test api-test parallel-test viz-test perf-test
	@echo "All tests completed"

# Run all examples
.PHONY: run-all
run-all: email-run data-run api-run parallel-run viz-run perf-run
	@echo "All examples completed"

# Start all Docker environments
.PHONY: docker-up-all
docker-up-all: email-docker-basic email-docker-mock
	@echo "All Docker environments started"

# Stop all Docker environments
.PHONY: docker-down-all
docker-down-all: email-docker-down
	@echo "All Docker environments stopped"

# Email Processing Examples
.PHONY: email-test
email-test:
	@echo "Running email processing tests..."
	@if [ ! -d "email_processing/tests" ]; then \
		echo "Creating tests directory in email_processing..."; \
		mkdir -p email_processing/tests; \
	fi
	$(EXPORT_PYTHONPATH) && cd email_processing && $(PYTHON) -m pytest tests/

.PHONY: email-run
email-run:
	@echo "Running email processing example..."
	$(EXPORT_PYTHONPATH) && cd email_processing && $(PYTHON) flow.py --mock

.PHONY: email-docker-basic
email-docker-basic:
	@echo "Starting basic email Docker environment..."
	cd email_processing && ./docker-up.sh basic

.PHONY: email-docker-mock
email-docker-mock:
	@echo "Starting mock email Docker environment..."
	cd email_processing && ./docker-up.sh mock

.PHONY: email-docker-full
email-docker-full:
	@echo "Starting full email Docker environment..."
	cd email_processing && ./docker-up.sh full

.PHONY: email-docker-down
email-docker-down:
	@echo "Stopping all email Docker environments..."
	cd email_processing && ./docker-down.sh all

# Data Processing Examples
.PHONY: data-test
data-test:
	@echo "Running data processing tests..."
	@if [ ! -d "data_processing/tests" ]; then \
		echo "Creating tests directory in data_processing..."; \
		mkdir -p data_processing/tests; \
	fi
	$(EXPORT_PYTHONPATH) && cd data_processing && $(PYTHON) -m pytest tests/

.PHONY: data-run
data-run:
	@echo "Running data processing example..."
	$(EXPORT_PYTHONPATH) && cd data_processing && $(PYTHON) data_processor.py

# API Integration Examples
.PHONY: api-test
api-test:
	@echo "Running API integration tests..."
	@if [ ! -d "api_integration/tests" ]; then \
		echo "Creating tests directory in api_integration..."; \
		mkdir -p api_integration/tests; \
	fi
	$(EXPORT_PYTHONPATH) && cd api_integration && $(PYTHON) -m pytest tests/

.PHONY: api-run
api-run:
	@echo "Running API integration example..."
	$(EXPORT_PYTHONPATH) && cd api_integration && $(PYTHON) api_client.py

# Parallel Tasks Examples
.PHONY: parallel-test
parallel-test:
	@echo "Running parallel tasks tests..."
	@if [ ! -d "parallel_tasks/tests" ]; then \
		echo "Creating tests directory in parallel_tasks..."; \
		mkdir -p parallel_tasks/tests; \
	fi
	$(EXPORT_PYTHONPATH) && cd parallel_tasks && $(PYTHON) -m pytest tests/

.PHONY: parallel-run
parallel-run:
	@echo "Running parallel tasks example..."
	$(EXPORT_PYTHONPATH) && cd parallel_tasks && $(PYTHON) parallel_processor.py

# Visualization Examples
.PHONY: viz-test
viz-test:
	@echo "Running visualization tests..."
	@if [ ! -d "visualization/tests" ]; then \
		echo "Creating tests directory in visualization..."; \
		mkdir -p visualization/tests; \
	fi
	$(EXPORT_PYTHONPATH) && cd visualization && $(PYTHON) -m pytest tests/

.PHONY: viz-run
viz-run:
	@echo "Running visualization example..."
	$(EXPORT_PYTHONPATH) && cd visualization && $(PYTHON) flow_visualizer.py

# Performance Benchmarks
.PHONY: perf-test
perf-test:
	@echo "Running performance benchmark tests..."
	@if [ ! -d "performance_benchmarks/tests" ]; then \
		echo "Creating tests directory in performance_benchmarks..."; \
		mkdir -p performance_benchmarks/tests; \
	fi
	$(EXPORT_PYTHONPATH) && cd performance_benchmarks && $(PYTHON) -m pytest tests/

.PHONY: perf-run
perf-run:
	@echo "Running performance benchmarks..."
	$(EXPORT_PYTHONPATH) && cd performance_benchmarks && $(PYTHON) run_benchmarks.py

# Utility Commands
.PHONY: clean
clean:
	@echo "Cleaning up temporary files..."
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	find . -name "*.log" -delete

.PHONY: update-viz
update-viz:
	@echo "Updating DSL visualizer in all Markdown files..."
	../scripts/add-dsl-visualizer.sh

# Show help by default
.DEFAULT_GOAL := help
