# Makefile for Document Processing System Documentation

# Variables
VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
UVICORN = $(VENV)/bin/uvicorn
PORT = 8000
HOST = 0.0.0.0

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help:
	@echo "Documentation System Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup         - Set up the development environment"
	@echo "  make install       - Install dependencies"
	@echo "  make run           - Run the development server"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Check code style with flake8"
	@echo "  make format        - Format code with black and isort"
	@echo "  make clean         - Clean up temporary files"
	@echo "  make clean-all     - Remove all generated files including venv"
	@echo "  make requirements  - Update requirements.txt"

# Setup virtual environment
.PHONY: setup
setup:
	@echo "Setting up virtual environment..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Install dependencies
.PHONY: install
install:
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt

# Run the development server
.PHONY: run
run:
	@echo "Starting development server on http://$(HOST):$(PORT)"
	$(UVICORN) app:app --reload --host $(HOST) --port $(PORT)

# Run tests
.PHONY: test
test:
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/

# Lint code
.PHONY: lint
lint:
	@echo "Checking code style..."
	$(VENV)/bin/flake8 app.py

# Format code
.PHONY: format
format:
	@echo "Formatting code..."
	$(VENV)/bin/black app.py
	$(VENV)/bin/isort app.py

# Clean up temporary files
.PHONY: clean
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type f -name "*.py[co]" -delete
	find . -type f -name "*~" -delete

# Remove all generated files including virtual environment
.PHONY: clean-all
clean-all: clean
	@echo "Removing virtual environment..."
	rm -rf $(VENV)

# Update requirements.txt
.PHONY: requirements
requirements:
	@echo "Updating requirements.txt..."
	$(PIP) freeze > requirements.txt

# Check if virtual environment exists
check_venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Ensure targets run with virtual environment
run test lint format requirements: check_venv
