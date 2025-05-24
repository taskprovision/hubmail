.PHONY: setup install run run-email run-server run-dashboard open-ui open-dashboard logs logs-follow test test-coverage test-email test-urgent-email test-report-email test-email-with-attachment docker-build docker-up docker-down docker-logs docker-shell docker-debug docker-test clean help

# Zmienne
PYTHON = python3
PIP = pip3
DOCKER_COMPOSE = docker-compose
BROWSER = xdg-open
PREFECT_UI_PORT = 4200
MAILHOG_UI_PORT = 8025
DASHBOARD_PORT = 8888

# Domyślny cel
.DEFAULT_GOAL := help

## Wyświetl pomoc
help:
	@echo "Dostępne komendy:"
	@echo "  make setup               - Przygotuj środowisko (utwórz .env, katalogi, itp.)"
	@echo "  make install             - Zainstaluj zależności"
	@echo "  make run                 - Uruchom cały system (email + Prefect UI)"
	@echo "  make run-email           - Uruchom tylko przepływ przetwarzania e-maili"
	@echo "  make run-server          - Uruchom tylko serwer Prefect"
	@echo "  make run-dashboard       - Uruchom dashboard webowy do monitorowania"
	@echo "  make open-ui             - Otwórz Prefect UI w przeglądarce"
	@echo "  make open-dashboard      - Otwórz dashboard webowy w przeglądarce"
	@echo "  make logs                - Wyświetl logi (opcjonalnie: FILTER=\"error\")"
	@echo "  make logs-follow         - Wyświetl logi w czasie rzeczywistym"
	@echo "  make test                - Uruchom testy (opcjonalnie: TEST=test_email_flow)"
	@echo "  make test-coverage       - Uruchom testy z pokryciem kodu"
	@echo "  make test-email          - Wyślij testowy e-mail"
	@echo "  make test-urgent-email   - Wyślij testowy pilny e-mail"
	@echo "  make test-report-email   - Wyślij testowy raport"
	@echo "  make test-email-with-attachment - Wyślij testowy e-mail z załącznikiem"
	@echo "  make docker-build        - Zbuduj obrazy Docker"
	@echo "  make docker-up           - Uruchom kontenery Docker"
	@echo "  make docker-down         - Zatrzymaj kontenery Docker"
	@echo "  make docker-logs         - Wyświetl logi kontenerów Docker"
	@echo "  make docker-shell        - Uruchom powłokę w kontenerze"
	@echo "  make docker-debug        - Uruchom przepływ w trybie debug w kontenerze (FLOW=nazwa_przepływu)"
	@echo "  make docker-test         - Uruchom testy w kontenerze Docker"
	@echo "  make clean               - Wyczyść pliki tymczasowe"

## Przygotuj środowisko
setup: .env
	@echo "Tworzenie katalogów..."
	@mkdir -p logs attachments test_data/attachments
	@echo "Tworzenie przykładowych załączników do testów..."
	@echo "To jest przykładowy plik tekstowy" > test_data/attachments/example.txt
	@echo "Data,Kategoria,Ilość,Wartość\n2025-05-01,Pilne,15,3500" > test_data/attachments/report.csv
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

## Uruchom cały system
run: .env
	@echo "Uruchamianie systemu..."
	@$(PYTHON) start.py

## Uruchom tylko przepływ przetwarzania e-maili
run-email: .env
	@echo "Uruchamianie przepływu przetwarzania e-maili..."
	@$(PYTHON) start.py --email-only

## Uruchom tylko serwer Prefect
run-server: .env
	@echo "Uruchamianie serwera Prefect..."
	@$(PYTHON) start.py --server-only

## Uruchom dashboard webowy
run-dashboard: .env
	@echo "Uruchamianie dashboardu webowego na porcie $(DASHBOARD_PORT)..."
	@$(PYTHON) dashboard.py --port $(DASHBOARD_PORT)

## Otwórz Prefect UI w przeglądarce
open-ui:
	@echo "Otwieranie Prefect UI w przeglądarce..."
	@$(BROWSER) http://localhost:$(PREFECT_UI_PORT) || echo "Nie można otworzyć przeglądarki. Otwórz ręcznie: http://localhost:$(PREFECT_UI_PORT)"

## Otwórz dashboard webowy w przeglądarce
open-dashboard:
	@echo "Otwieranie dashboardu webowego w przeglądarce..."
	@$(BROWSER) http://localhost:$(DASHBOARD_PORT) || echo "Nie można otworzyć przeglądarki. Otwórz ręcznie: http://localhost:$(DASHBOARD_PORT)"

## Wyświetl logi
logs:
	@if [ -z "$(FILTER)" ]; then \
		echo "Wyświetlanie wszystkich logów..."; \
		cat logs/email_flow_*.log | sort; \
	else \
		echo "Wyświetlanie logów z filtrem: $(FILTER)"; \
		cat logs/email_flow_*.log | grep -i "$(FILTER)" | sort; \
	fi

## Wyświetl logi w czasie rzeczywistym
logs-follow:
	@echo "Wyświetlanie logów w czasie rzeczywistym..."
	@tail -f logs/email_flow_*.log

## Uruchom testy
test:
	@echo "Uruchamianie testów..."
	@if [ -z "$(TEST)" ]; then \
		$(PYTHON) -m pytest tests/ -v; \
	else \
		$(PYTHON) -m pytest tests/$(TEST).py -v; \
	fi

## Uruchom testy z pokryciem kodu
test-coverage:
	@echo "Uruchamianie testów z pokryciem kodu..."
	@$(PYTHON) -m pytest tests/ --cov=. --cov-report=term --cov-report=html
	@echo "Raport pokrycia kodu dostępny w htmlcov/index.html"

## Wyślij testowy e-mail
test-email:
	@echo "Wysyłanie testowego e-maila..."
	@$(PYTHON) test_data/send_test_email.py

## Wyślij testowy pilny e-mail
test-urgent-email:
	@echo "Wysyłanie testowego pilnego e-maila..."
	@$(PYTHON) test_data/send_test_email.py --urgent

## Wyślij testowy raport
test-report-email:
	@echo "Wysyłanie testowego raportu..."
	@$(PYTHON) test_data/send_test_email.py --report

## Wyślij testowy e-mail z załącznikiem
test-email-with-attachment:
	@echo "Wysyłanie testowego e-maila z załącznikiem..."
	@$(PYTHON) test_data/send_test_email.py --attachments 2

## Zbuduj obrazy Docker
docker-build:
	@echo "Budowanie obrazów Docker..."
	@$(DOCKER_COMPOSE) build

## Uruchom kontenery Docker
docker-up: .env
	@echo "Uruchamianie kontenerów Docker..."
	@$(DOCKER_COMPOSE) up -d
	@echo "Kontenery uruchomione."
	@echo "Prefect UI dostępny pod adresem: http://localhost:$(PREFECT_UI_PORT)"
	@echo "MailHog (serwer SMTP/IMAP) dostępny pod adresem: http://localhost:$(MAILHOG_UI_PORT)"

## Zatrzymaj kontenery Docker
docker-down:
	@echo "Zatrzymywanie kontenerów Docker..."
	@$(DOCKER_COMPOSE) down

## Wyświetl logi kontenerów Docker
docker-logs:
	@echo "Wyświetlanie logów kontenerów Docker..."
	@$(DOCKER_COMPOSE) logs -f

## Uruchom powłokę w kontenerze
docker-shell:
	@echo "Uruchamianie powłoki w kontenerze..."
	@$(DOCKER_COMPOSE) exec hubmail bash

## Uruchom przepływ w trybie debug w kontenerze
docker-debug:
	@if [ -z "$(FLOW)" ]; then \
		echo "Podaj nazwę przepływu: make docker-debug FLOW=nazwa_przepływu"; \
	else \
		echo "Uruchamianie przepływu $(FLOW) w trybie debug..."; \
		$(DOCKER_COMPOSE) exec hubmail python -m debugpy --listen 0.0.0.0:5678 email_flows.py --flow $(FLOW); \
	fi

## Uruchom testy w kontenerze Docker
docker-test:
	@echo "Uruchamianie testów w kontenerze Docker..."
	@$(DOCKER_COMPOSE) exec hubmail python -m pytest tests/ -v

## Wyczyść pliki tymczasowe
clean:
	@echo "Czyszczenie plików tymczasowych..."
	@rm -rf __pycache__ .pytest_cache .coverage htmlcov
	@find . -name "*.pyc" -delete
	@echo "Pliki tymczasowe wyczyszczone."
