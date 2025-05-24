.PHONY: help install dev stop restart restart-config status logs app-logs config-logs debug-config ui config-ui dashboard all-ui python-deps update-env clean test python-tests python-docs generate-workflow-diagram backup restore check-api mini-dashboard notifications scheduler parallel-run example-basic example-email example-data example-api example-sentiment example-parallel example-scheduled lint type-check format tox build publish publish-test

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
	@echo '  example-basic Run basic flow example'
	@echo '  example-email Run email processing example'
	@echo '  example-data  Run data processing example'
	@echo '  example-api   Run API integration example'
	@echo '  example-sentiment Run sentiment analysis example'
	@echo '  example-parallel Run parallel execution example'
	@echo '  example-scheduled Run scheduled flow example'
	@echo '  lint          Run linting checks with flake8, black, and isort'
	@echo '  type-check    Run type checking with mypy'
	@echo '  format        Format code with black and isort'
	@echo '  tox           Run tests with tox in multiple environments'
	@echo '  build         Build package distributions'
	@echo '  publish       Publish package to PyPI'
	@echo '  publish-test  Publish package to TestPyPI'

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

## Start mini dashboard
mini-dashboard:
	@echo -e "Uruchamianie Mini Dashboardu..."
	cd dsl && python mini_dashboard.py

## Configure notifications
notifications:
	@echo -e "Konfiguracja powiadomień..."
	cd dsl && python -c "from notification_service import load_config, save_config; config = load_config(); print('Aktualna konfiguracja:', config); print('Aby włączyć powiadomienia, edytuj plik config/notification_config.json')"

## Start scheduler
scheduler:
	@echo -e "Uruchamianie planera przepływów..."
	cd dsl && python flow_scheduler.py start

## Run flow with parallel execution
parallel-run:
	@echo -e "Uruchamianie przepływu z równoległym wykonaniem..."
	@echo -e "Użycie: make parallel-run FLOW=nazwa_pliku.dsl"
	cd dsl && python -c "from parallel_executor import run_parallel_flow_from_dsl; from flow_dsl import load_dsl; dsl_content = load_dsl('dsl_definitions/$(FLOW)'); result = run_parallel_flow_from_dsl(dsl_content, {}); print('Wynik:', result)"

## Run basic flow example
example-basic:
	@echo -e "Uruchamianie podstawowego przykładu przepływu..."
	mkdir -p examples
	cat > examples/basic_flow.py << 'EOL'
from flow_dsl import task, run_flow_from_dsl

@task(name="Zadanie 1")
def task1(input_data):
    print("Wykonuję zadanie 1")
    return {"result": input_data + " - przetworzony przez zadanie 1"}

@task(name="Zadanie 2")
def task2(input_data):
    print("Wykonuję zadanie 2")
    return {"result": input_data["result"] + " - przetworzony przez zadanie 2"}

@task(name="Zadanie 3")
def task3(input_data):
    print("Wykonuję zadanie 3")
    return {"result": input_data["result"] + " - przetworzony przez zadanie 3"}

# Definicja przepływu DSL
flow_dsl = """
flow SimpleFlow:
    description: "Prosty przepływ sekwencyjny"
    task1 -> task2
    task2 -> task3
"""

# Uruchomienie przepływu
results = run_flow_from_dsl(flow_dsl, "Dane wejściowe")
print("\nWyniki przepływu:")
print(results)
EOL
	python examples/basic_flow.py

## Run email processing example
example-email:
	@echo -e "Uruchamianie przykładu przetwarzania emaili..."
	mkdir -p examples
	cat > examples/email_flow.py << 'EOL'
from flow_dsl import task, run_flow_from_dsl

@task(name="Pobieranie emaili")
def fetch_emails(server, username, password):
    print(f"Pobieranie emaili z {server} jako {username}")
    # Symulacja pobierania emaili
    emails = [
        {"id": "1", "subject": "Pytanie o wsparcie", "urgent": True},
        {"id": "2", "subject": "Newsletter", "urgent": False},
        {"id": "3", "subject": "Pilna sprawa", "urgent": True}
    ]
    return emails

@task(name="Klasyfikacja emaili")
def classify_emails(emails):
    print(f"Klasyfikacja {len(emails)} emaili")
    urgent = [email for email in emails if email.get("urgent", False)]
    regular = [email for email in emails if not email.get("urgent", False)]
    return {"urgent_emails": urgent, "regular_emails": regular}

@task(name="Przetwarzanie pilnych emaili")
def process_urgent_emails(urgent_emails):
    print(f"Przetwarzanie {len(urgent_emails)} pilnych emaili")
    return [f"Odpowiedź na pilny email {email['id']}" for email in urgent_emails]

@task(name="Przetwarzanie zwykłych emaili")
def process_regular_emails(regular_emails):
    print(f"Przetwarzanie {len(regular_emails)} zwykłych emaili")
    return [f"Odpowiedź na zwykły email {email['id']}" for email in regular_emails]

# Definicja przepływu DSL
email_dsl = """
flow EmailProcessing:
    description: "Przetwarzanie e-maili"
    fetch_emails -> classify_emails
    classify_emails -> process_urgent_emails
    classify_emails -> process_regular_emails
"""

# Uruchomienie przepływu
results = run_flow_from_dsl(email_dsl, {
    "server": "imap.example.com",
    "username": "info@example.com",
    "password": "password123"
})
print("\nWyniki przepływu:")
print(results)
EOL
	python examples/email_flow.py

## Run data processing example
example-data:
	@echo -e "Uruchamianie przykładu przetwarzania danych..."
	mkdir -p examples/data
	cat > examples/data/sample.csv << 'EOL'
id,name,value
1,Product A,100
2,Product B,200
3,Product A,150
4,Product C,300
5,Product B,250
EOL
	cat > examples/data_flow.py << 'EOL'
from flow_dsl import task, run_flow_from_dsl
import pandas as pd
import os

@task(name="Wczytanie CSV")
def load_csv(file_path):
    print(f"Wczytywanie danych z {file_path}")
    df = pd.read_csv(file_path)
    return {"dataframe": df}

@task(name="Czyszczenie danych")
def clean_data(input_data):
    df = input_data["dataframe"]
    print(f"Czyszczenie danych, początkowy rozmiar: {len(df)}")
    # Usunięcie duplikatów
    df = df.drop_duplicates()
    print(f"Rozmiar po usunięciu duplikatów: {len(df)}")
    return {"dataframe": df}

@task(name="Transformacja danych")
def transform_data(input_data):
    df = input_data["dataframe"]
    print(f"Transformacja danych")
    # Przykładowa transformacja - konwersja kolumny na wielkie litery
    if "name" in df.columns:
        df["name"] = df["name"].str.upper()
    # Dodanie nowej kolumny
    df["tax"] = df["value"] * 0.23
    return {"dataframe": df}

@task(name="Zapisanie wyników")
def save_results(input_data, output_path):
    df = input_data["dataframe"]
    print(f"Zapisywanie wyników do {output_path}")
    df.to_csv(output_path, index=False)
    return {"rows_count": len(df), "output_path": output_path}

# Definicja przepływu DSL
flow_dsl = """
flow CSVProcessing:
    description: "Przetwarzanie pliku CSV"
    load_csv -> clean_data
    clean_data -> transform_data
    transform_data -> save_results
"""

# Upewnienie się, że katalog wyjściowy istnieje
os.makedirs("examples/data/output", exist_ok=True)

# Uruchomienie przepływu
results = run_flow_from_dsl(flow_dsl, {
    "file_path": "examples/data/sample.csv",
    "output_path": "examples/data/output/processed.csv"
})
print("\nWyniki przepływu:")
print(results)

# Wyświetlenie przetworzonego pliku
print("\nZawartość przetworzonego pliku:")
processed_df = pd.read_csv("examples/data/output/processed.csv")
print(processed_df)
EOL
	python examples/data_flow.py

## Run API integration example
example-api:
	@echo -e "Uruchamianie przykładu integracji z API..."
	mkdir -p examples
	cat > examples/api_flow.py << 'EOL'
from flow_dsl import task, run_flow_from_dsl
import requests
import json
import os
import sqlite3

@task(name="Pobieranie danych z API")
def fetch_from_api(api_url):
    print(f"Pobieranie danych z {api_url}")
    try:
        # Symulacja odpowiedzi API
        data = [
            {"id": 1, "name": "Item 1", "value": 100},
            {"id": 2, "name": "Item 2", "value": 200},
            {"id": 3, "name": "Item 3", "value": 300},
            {"id": 4, "name": "Item 4", "value": 400},
            {"id": 5, "name": "Item 5", "value": 500}
        ]
        print(f"Pobrano {len(data)} elementów")
        return {"data": data}
    except Exception as e:
        print(f"Błąd podczas pobierania danych: {str(e)}")
        return {"data": [], "error": str(e)}

@task(name="Przetwarzanie danych")
def process_api_data(input_data):
    data = input_data["data"]
    print(f"Przetwarzanie {len(data)} elementów")
    # Przykładowe przetwarzanie - ekstrakcja potrzebnych pól
    processed = []
    for item in data:
        if "value" in item:
            processed.append({
                "id": item["id"],
                "name": item["name"],
                "value": item["value"],
                "category": "high" if item["value"] > 250 else "low"
            })
    print(f"Przetworzono {len(processed)} elementów")
    return {"processed_data": processed}

@task(name="Zapisanie do bazy danych")
def save_to_database(input_data, db_path):
    processed_data = input_data["processed_data"]
    print(f"Zapisywanie {len(processed_data)} elementów do bazy danych {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Utworzenie tabeli, jeśli nie istnieje
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT,
        value REAL,
        category TEXT
    )
    ''')
    
    # Wstawienie danych
    for item in processed_data:
        cursor.execute(
            "INSERT OR REPLACE INTO items (id, name, value, category) VALUES (?, ?, ?, ?)",
            (item["id"], item["name"], item["value"], item["category"])
        )
    
    conn.commit()
    
    # Sprawdzenie, ile rekordów jest w bazie
    cursor.execute("SELECT COUNT(*) FROM items")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    return {"items_saved": len(processed_data), "total_items": count}

# Definicja przepływu DSL
flow_dsl = """
flow APIToDatabaseFlow:
    description: "Pobieranie danych z API i zapisywanie do bazy danych"
    fetch_from_api -> process_api_data
    process_api_data -> save_to_database
"""

# Upewnienie się, że katalog wyjściowy istnieje
os.makedirs("examples/data", exist_ok=True)

# Uruchomienie przepływu
results = run_flow_from_dsl(flow_dsl, {
    "api_url": "https://api.example.com/data",
    "db_path": "examples/data/database.sqlite"
})
print("\nWyniki przepływu:")
print(results)

# Wyświetlenie zawartości bazy danych
print("\nZawartość bazy danych:")
conn = sqlite3.connect("examples/data/database.sqlite")
cursor = conn.cursor()
cursor.execute("SELECT * FROM items")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()
EOL
	python examples/api_flow.py

## Run sentiment analysis example
example-sentiment:
	@echo -e "Uruchamianie przykładu analizy sentymentu..."
	mkdir -p examples/data
	cat > examples/data/texts.txt << 'EOL'
To jest świetny produkt, jestem bardzo zadowolony z zakupu!
Niestety produkt nie spełnił moich oczekiwań, jestem rozczarowany.
Produkt jest ok, ale cena jest zbyt wysoka.
Uwielbiam ten produkt, polecam wszystkim!
Fatalna obsługa klienta, nigdy więcej nie kupię nic w tym sklepie.
EOL
	cat > examples/sentiment_flow.py << 'EOL'
from flow_dsl import task, run_flow_from_dsl
import os

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    nltk.download('vader_lexicon', quiet=True)
except ImportError:
    print("Instalowanie wymaganych pakietów...")
    import subprocess
    subprocess.call(["pip", "install", "nltk"])
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    nltk.download('vader_lexicon', quiet=True)

@task(name="Inicjalizacja analizatora")
def init_analyzer():
    print("Inicjalizacja analizatora sentymentu")
    analyzer = SentimentIntensityAnalyzer()
    return {"analyzer": analyzer}

@task(name="Wczytanie tekstów")
def load_texts(file_path):
    print(f"Wczytywanie tekstów z {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        texts = [line.strip() for line in f if line.strip()]
    print(f"Wczytano {len(texts)} tekstów")
    return {"texts": texts}

@task(name="Analiza sentymentu")
def analyze_sentiment(analyzer_data, texts_data):
    analyzer = analyzer_data["analyzer"]
    texts = texts_data["texts"]
    print(f"Analiza sentymentu dla {len(texts)} tekstów")
    
    results = []
    for text in texts:
        scores = analyzer.polarity_scores(text)
        sentiment = "positive" if scores["compound"] > 0.05 else "negative" if scores["compound"] < -0.05 else "neutral"
        results.append({
            "text": text,
            "sentiment": sentiment,
            "scores": scores
        })
    
    return {"sentiment_results": results}

@task(name="Generowanie raportu")
def generate_report(input_data):
    results = input_data["sentiment_results"]
    print("Generowanie raportu")
    
    positive_count = sum(1 for r in results if r["sentiment"] == "positive")
    negative_count = sum(1 for r in results if r["sentiment"] == "negative")
    neutral_count = sum(1 for r in results if r["sentiment"] == "neutral")
    
    report = {
        "total_texts": len(results),
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
        "positive_percentage": (positive_count / len(results)) * 100 if results else 0,
        "negative_percentage": (negative_count / len(results)) * 100 if results else 0,
        "neutral_percentage": (neutral_count / len(results)) * 100 if results else 0
    }
    
    return {"report": report}

# Definicja przepływu DSL
flow_dsl = """
flow SentimentAnalysis:
    description: "Analiza sentymentu tekstu"
    init_analyzer -> analyze_sentiment
    load_texts -> analyze_sentiment
    analyze_sentiment -> generate_report
"""

# Uruchomienie przepływu
results = run_flow_from_dsl(flow_dsl, {
    "file_path": "examples/data/texts.txt"
})
print("\nWyniki przepływu:")
print(results)

# Wyświetlenie szczegółowych wyników
print("\nSzczegółowe wyniki analizy sentymentu:")
for result in results["analyze_sentiment"]["sentiment_results"]:
    print(f"Tekst: {result['text']}")
    print(f"Sentyment: {result['sentiment']}")
    print(f"Oceny: {result['scores']}")
    print()

print("Podsumowanie:")
report = results["generate_report"]["report"]
print(f"Pozytywne: {report['positive_count']} ({report['positive_percentage']:.1f}%)")
print(f"Negatywne: {report['negative_count']} ({report['negative_percentage']:.1f}%)")
print(f"Neutralne: {report['neutral_count']} ({report['neutral_percentage']:.1f}%)")
EOL
	python examples/sentiment_flow.py

## Run parallel execution example
example-parallel:
	@echo -e "Uruchamianie przykładu równoległego wykonania..."
	mkdir -p examples/data/files
	# Tworzenie przykładowych plików
	for i in {1..5}; do \
		echo "To jest zawartość pliku $i.\nZawiera kilka linii tekstu.\nSłuży do testowania równoległego przetwarzania." > examples/data/files/file$$i.txt; \
	done
	cat > examples/parallel_flow.py << 'EOL'
from flow_dsl import task
from parallel_executor import run_parallel_flow_from_dsl
import os
import time

@task(name="Skanowanie katalogu")
def scan_directory(directory_path):
    print(f"Skanowanie katalogu {directory_path}")
    files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) 
             if os.path.isfile(os.path.join(directory_path, f))]
    print(f"Znaleziono {len(files)} plików")
    return {"files": files}

@task(name="Przetwarzanie pliku")
def process_file(file_path):
    print(f"Przetwarzanie pliku {file_path}")
    # Symulacja dłuższego przetwarzania
    time.sleep(1)
    
    # Zliczanie linii w pliku
    with open(file_path, 'r', encoding='utf-8') as f:
        line_count = sum(1 for _ in f)
    
    # Zliczanie słów w pliku
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        word_count = len(content.split())
    
    return {
        "file_path": file_path,
        "file_name": os.path.basename(file_path),
        "line_count": line_count,
        "word_count": word_count,
        "size_bytes": os.path.getsize(file_path)
    }

@task(name="Agregacja wyników")
def aggregate_results(processed_files):
    print("Agregacja wyników")
    total_files = len(processed_files)
    total_lines = sum(file_data["line_count"] for file_data in processed_files)
    total_words = sum(file_data["word_count"] for file_data in processed_files)
    total_size = sum(file_data["size_bytes"] for file_data in processed_files)
    
    return {
        "total_files": total_files,
        "total_lines": total_lines,
        "total_words": total_words,
        "total_size_bytes": total_size,
        "average_lines": total_lines / total_files if total_files > 0 else 0,
        "average_words": total_words / total_files if total_files > 0 else 0,
        "files_details": processed_files
    }

# Definicja przepływu DSL z równoległym wykonaniem
flow_dsl = """
flow ParallelFileProcessing:
    description: "Równoległe przetwarzanie plików"
    scan_directory -> process_file
    process_file -> aggregate_results
"""

# Porównanie czasu wykonania sekwencyjnego i równoległego
print("Uruchamianie przepływu sekwencyjnie...")
start_time = time.time()
from flow_dsl import run_flow_from_dsl
seq_results = run_flow_from_dsl(flow_dsl, {
    "directory_path": "examples/data/files"
})
seq_time = time.time() - start_time
print(f"Czas wykonania sekwencyjnego: {seq_time:.2f}s")

print("\nUruchamianie przepływu równolegle...")
start_time = time.time()
par_results = run_parallel_flow_from_dsl(flow_dsl, {
    "directory_path": "examples/data/files"
}, max_workers=4)
par_time = time.time() - start_time
print(f"Czas wykonania równoległego: {par_time:.2f}s")

print(f"\nPrzyspieszenie: {seq_time/par_time:.2f}x")

print("\nWyniki agregacji:")
aggregated = par_results["aggregate_results"]
print(f"Liczba plików: {aggregated['total_files']}")
print(f"Liczba linii: {aggregated['total_lines']}")
print(f"Liczba słów: {aggregated['total_words']}")
print(f"Rozmiar: {aggregated['total_size_bytes']} bajtów")
print(f"\nSzczegóły plików:")
for file_data in aggregated["files_details"]:
    print(f"- {file_data['file_name']}: {file_data['line_count']} linii, {file_data['word_count']} słów, {file_data['size_bytes']} bajtów")
EOL
	python examples/parallel_flow.py

## Run scheduled flow example
example-scheduled:
	@echo -e "Uruchamianie przykładu planowania przepływów..."
	mkdir -p examples/dsl_definitions
	cat > examples/dsl_definitions/daily_report.dsl << 'EOL'
flow DailyReport:
    description: "Generowanie codziennego raportu"
    fetch_data -> process_data
    process_data -> generate_report
    generate_report -> send_notification
EOL
	cat > examples/scheduled_flow.py << 'EOL'
from flow_dsl import task, run_flow_from_dsl, load_dsl
import datetime
import time
import os

@task(name="Pobieranie danych")
def fetch_data(date):
    print(f"Pobieranie danych dla {date}")
    # Symulacja pobierania danych
    data = [
        {"id": 1, "product": "Produkt A", "sales": 100, "revenue": 1000},
        {"id": 2, "product": "Produkt B", "sales": 50, "revenue": 750},
        {"id": 3, "product": "Produkt C", "sales": 75, "revenue": 1500}
    ]
    return {"data": data, "date": date}

@task(name="Przetwarzanie danych")
def process_data(input_data):
    data = input_data["data"]
    date = input_data["date"]
    print(f"Przetwarzanie {len(data)} rekordów danych dla {date}")
    
    # Obliczanie dodatkowych metryki
    for item in data:
        item["avg_price"] = item["revenue"] / item["sales"] if item["sales"] > 0 else 0
    
    # Sortowanie po przychodach
    data.sort(key=lambda x: x["revenue"], reverse=True)
    
    return {"processed_data": data, "date": date}

@task(name="Generowanie raportu")
def generate_report(input_data):
    processed_data = input_data["processed_data"]
    date = input_data["date"]
    print(f"Generowanie raportu dla {date}")
    
    # Obliczanie podsumowań
    total_sales = sum(item["sales"] for item in processed_data)
    total_revenue = sum(item["revenue"] for item in processed_data)
    avg_price = total_revenue / total_sales if total_sales > 0 else 0
    
    # Tworzenie raportu
    report = {
        "date": date,
        "total_products": len(processed_data),
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "avg_price": avg_price,
        "top_product": processed_data[0]["product"] if processed_data else None,
        "products_summary": processed_data
    }
    
    # Zapisywanie raportu do pliku
    os.makedirs("examples/reports", exist_ok=True)
    report_file = f"examples/reports/report_{date}.txt"
    with open(report_file, "w") as f:
        f.write(f"Raport sprzedaży za {date}\n")
        f.write(f"===========================\n\n")
        f.write(f"Liczba produktów: {report['total_products']}\n")
        f.write(f"Liczba sprzedaży: {report['total_sales']}\n")
        f.write(f"Przychód: {report['total_revenue']} PLN\n")
        f.write(f"Średnia cena: {report['avg_price']:.2f} PLN\n")
        f.write(f"Najlepiej sprzedający się produkt: {report['top_product']}\n\n")
        f.write(f"Szczegóły produktów:\n")
        for product in report["products_summary"]:
            f.write(f"- {product['product']}: {product['sales']} szt., {product['revenue']} PLN, średnia cena: {product['avg_price']:.2f} PLN\n")
    
    return {"report": report, "report_file": report_file}

@task(name="Wysyłanie powiadomienia")
def send_notification(input_data):
    report = input_data["report"]
    report_file = input_data["report_file"]
    print(f"Wysyłanie powiadomienia o raporcie za {report['date']}")
    
    # Symulacja wysyłania powiadomienia
    print(f"Powiadomienie: Raport sprzedaży za {report['date']} jest gotowy.")
    print(f"Raport zapisany w pliku: {report_file}")
    
    return {"notification_sent": True, "timestamp": datetime.datetime.now().isoformat()}

# Symulacja planera
class SimpleScheduler:
    def __init__(self):
        self.schedules = []
    
    def add_schedule(self, dsl_file, interval=None, daily=None, input_data=None):
        schedule_id = f"schedule_{len(self.schedules) + 1}"
        schedule = {
            "id": schedule_id,
            "dsl_file": dsl_file,
            "interval": interval,  # w sekundach
            "daily": daily,  # format "HH:MM"
            "input_data": input_data or {},
            "next_run": self._calculate_next_run(interval, daily),
            "last_run": None
        }
        self.schedules.append(schedule)
        return schedule_id
    
    def _calculate_next_run(self, interval, daily):
        now = datetime.datetime.now()
        if interval:
            return now + datetime.timedelta(seconds=interval)
        elif daily:
            hour, minute = map(int, daily.split(":"))
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += datetime.timedelta(days=1)
            return next_run
        return now
    
    def list_schedules(self):
        return self.schedules
    
    def run_due_schedules(self):
        now = datetime.datetime.now()
        for schedule in self.schedules:
            if schedule["next_run"] <= now:
                print(f"Uruchamianie zaplanowanego przepływu {schedule['id']}")
                try:
                    dsl_content = load_dsl(schedule["dsl_file"])
                    # Dodanie daty do danych wejściowych
                    input_data = schedule["input_data"].copy()
                    input_data["date"] = now.strftime("%Y-%m-%d")
                    result = run_flow_from_dsl(dsl_content, input_data)
                    schedule["last_run"] = now
                    schedule["last_result"] = {"success": True, "result": result}
                except Exception as e:
                    schedule["last_run"] = now
                    schedule["last_result"] = {"success": False, "error": str(e)}
                
                # Aktualizacja czasu następnego uruchomienia
                schedule["next_run"] = self._calculate_next_run(schedule["interval"], schedule["daily"])

# Tworzenie i uruchamianie planera
print("Tworzenie planera przepływów...")
scheduler = SimpleScheduler()

# Dodanie harmonogramu co 10 sekund
schedule_id1 = scheduler.add_schedule(
    "examples/dsl_definitions/daily_report.dsl",
    interval=10,
    input_data={"date": datetime.datetime.now().strftime("%Y-%m-%d")}
)

# Dodanie harmonogramu codziennego o określonej godzinie
current_time = datetime.datetime.now()
minute = (current_time.minute + 1) % 60  # Następna minuta
hour = current_time.hour + (1 if minute == 0 else 0) % 24
daily_time = f"{hour:02d}:{minute:02d}"
schedule_id2 = scheduler.add_schedule(
    "examples/dsl_definitions/daily_report.dsl",
    daily=daily_time,
    input_data={"date": datetime.datetime.now().strftime("%Y-%m-%d")}
)

print("Harmonogramy:")
for schedule in scheduler.list_schedules():
    next_run = schedule["next_run"].strftime("%Y-%m-%d %H:%M:%S")
    if schedule["interval"]:
        print(f"- {schedule['id']}: co {schedule['interval']} sekund, następne uruchomienie: {next_run}")
    elif schedule["daily"]:
        print(f"- {schedule['id']}: codziennie o {schedule['daily']}, następne uruchomienie: {next_run}")

# Symulacja działania planera przez 15 sekund
print("\nUruchamianie planera na 15 sekund...")
start_time = time.time()
while time.time() - start_time < 15:
    scheduler.run_due_schedules()
    time.sleep(1)

print("\nPodsumowanie wykonanych przepływów:")
for schedule in scheduler.list_schedules():
    if schedule["last_run"]:
        last_run = schedule["last_run"].strftime("%Y-%m-%d %H:%M:%S")
        success = schedule["last_result"]["success"]
        status = "sukces" if success else "błąd"
        print(f"- {schedule['id']}: ostatnie uruchomienie: {last_run}, status: {status}")
        if success:
            result = schedule["last_result"]["result"]
            report = result["generate_report"]["report"]
            print(f"  Raport: {report['total_products']} produktów, {report['total_sales']} sprzedaży, {report['total_revenue']} PLN przychodu")
EOL
	python examples/scheduled_flow.py

## Run linting checks with flake8, black, and isort
lint:
	@echo -e "Running linting checks..."
	flake8 taskinity tests
	black --check taskinity tests
	isort --check-only --profile black taskinity tests

## Run type checking with mypy
type-check:
	@echo -e "Running type checking..."
	mypy taskinity

## Format code with black and isort
format:
	@echo -e "Formatting code..."
	black taskinity tests
	isort --profile black taskinity tests

## Run tests with tox in multiple environments
tox:
	@echo -e "Running tests with tox..."
	tox

## Build package distributions
build:
	@echo -e "Building package distributions..."
	poetry build

## Publish package to PyPI
publish: build
	@echo -e "Publishing package to PyPI..."
	poetry version patch
	poetry publish --build

## Publish package to TestPyPI
publish-test: build
	@echo -e "Publishing package to TestPyPI..."
	poetry publish -r testpypi

## Show help by default
.DEFAULT_GOAL := help
