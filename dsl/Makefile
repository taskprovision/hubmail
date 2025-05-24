# Makefile for Taskinity DSL examples and tests

.PHONY: help install test test-basic test-email example-basic example-email example-data example-api

## Display help information
help:
	@echo "Taskinity DSL Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  help             - Display this help message"
	@echo "  install          - Install dependencies"
	@echo "  test             - Run all tests"
	@echo "  test-basic       - Run basic tests"
	@echo "  test-email       - Run email processing tests"
	@echo "  example-basic    - Run basic flow example"
	@echo "  example-email    - Run email processing example"
	@echo "  example-data     - Run data processing example"
	@echo "  example-api      - Run API integration example"

## Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

## Run all tests
test:
	@echo "Running all tests..."
	pytest -xvs tests/

## Run basic tests
test-basic:
	@echo "Running basic tests..."
	pytest -xvs tests/test_basic.py

## Run email processing tests
test-email:
	@echo "Running email processing tests..."
	pytest -xvs examples/email_processing/tests/

## Run basic flow example
example-basic:
	@echo -e "Running basic flow example..."
	python examples/basic_flow.py --mock

## Run email processing example
example-email:
	@echo -e "Running email processing example..."
	python examples/email_flow.py --mock

## Run data processing example
example-data:
	@echo -e "Running data processing example..."
	python examples/data_flow.py --mock

## Run API integration example
example-api:
	@echo -e "Running API integration example..."
	python examples/api_flow.py --mock
