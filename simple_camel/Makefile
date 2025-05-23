.PHONY: setup install test run run-email run-dashboard docker-build docker-up docker-down docker-logs test-send-email test-send-urgent test-send-report clean help

# Zmienne
PYTHON = python3
PIP = pip3
DOCKER_COMPOSE = docker-compose

# Domyślny cel
.DEFAULT_GOAL := help

## Wyświetl pomoc
help:
	@echo "Dostępne komendy:"
	@echo "  make setup          - Przygotuj środowisko (utwórz .env, katalogi, itp.)"
	@echo "  make install        - Zainstaluj zależności"
	@echo "  make test           - Uruchom testy"
	@echo "  make run            - Uruchom cały system (email + dashboard)"
	@echo "  make run-email      - Uruchom tylko przetwarzanie e-maili"
	@echo "  make run-dashboard  - Uruchom tylko dashboard"
	@echo "  make docker-build   - Zbuduj obrazy Docker"
	@echo "  make docker-up      - Uruchom kontenery Docker"
	@echo "  make docker-down    - Zatrzymaj kontenery Docker"
	@echo "  make docker-logs    - Pokaż logi kontenerów Docker"
	@echo "  make test-send-email - Wyślij testowy e-mail"
	@echo "  make test-send-urgent - Wyślij testowy pilny e-mail"
	@echo "  make test-send-report - Wyślij testowy raport"
	@echo "  make clean          - Wyczyść pliki tymczasowe"

## Przygotuj środowisko
setup: .env
	@echo "Tworzenie katalogów..."
	@mkdir -p attachments logs static templates test_data/attachments
	@echo "Tworzenie przykładowych załączników do testów..."
	@echo "To jest przykładowy plik tekstowy" > test_data/attachments/example.txt
	@echo "To jest przykładowy dokument" > test_data/attachments/document.doc
	@echo "Środowisko przygotowane."

## Utwórz plik .env jeśli nie istnieje
.env:
	@if [ ! -f .env ]; then \
		echo "Tworzenie pliku .env z .env.example..."; \
		cp .env.example .env; \
		echo "Plik .env utworzony. Dostosuj go do swoich potrzeb."; \
	fi

## Zainstaluj zależności
install:
	@echo "Instalowanie zależności..."
	@$(PIP) install -r requirements.txt
	@echo "Zależności zainstalowane."

## Uruchom testy
test:
	@echo "Uruchamianie testów..."
	@$(PYTHON) -m pytest tests/

## Uruchom cały system
run: .env
	@echo "Uruchamianie systemu..."
	@$(PYTHON) start.py

## Uruchom tylko przetwarzanie e-maili
run-email: .env
	@echo "Uruchamianie przetwarzania e-maili..."
	@$(PYTHON) start.py --email-only

## Uruchom tylko dashboard
run-dashboard: .env
	@echo "Uruchamianie dashboardu..."
	@$(PYTHON) start.py --dashboard-only

## Zbuduj obrazy Docker
docker-build:
	@echo "Budowanie obrazów Docker..."
	@$(DOCKER_COMPOSE) build

## Uruchom kontenery Docker
docker-up: .env
	@echo "Uruchamianie kontenerów Docker..."
	@$(DOCKER_COMPOSE) up -d
	@echo "Kontenery uruchomione. Dashboard dostępny pod adresem: http://localhost:8000"
	@echo "MailHog (serwer SMTP/IMAP) dostępny pod adresem: http://localhost:8025"

## Zatrzymaj kontenery Docker
docker-down:
	@echo "Zatrzymywanie kontenerów Docker..."
	@$(DOCKER_COMPOSE) down

## Pokaż logi kontenerów Docker
docker-logs:
	@echo "Wyświetlanie logów kontenerów Docker..."
	@$(DOCKER_COMPOSE) logs -f

## Wyślij testowy e-mail
test-send-email:
	@echo "Wysyłanie testowego e-maila..."
	@$(PYTHON) test_data/send_test_email.py

## Wyślij testowy pilny e-mail
test-send-urgent:
	@echo "Wysyłanie testowego pilnego e-maila..."
	@$(PYTHON) test_data/send_test_email.py --urgent

## Wyślij testowy raport
test-send-report:
	@echo "Wysyłanie testowego raportu..."
	@$(PYTHON) test_data/send_test_email.py --report

## Wyczyść pliki tymczasowe
clean:
	@echo "Czyszczenie plików tymczasowych..."
	@rm -rf __pycache__ .pytest_cache
	@find . -name "*.pyc" -delete
	@echo "Pliki tymczasowe wyczyszczone."
