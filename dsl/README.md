# Taskinity - Intelligent Task Orchestration Framework

Taskinity is a modern framework for defining, managing, and monitoring task flows using an intuitive DSL and Python decorators. Designed with simplicity and efficiency in mind, Taskinity offers significantly less overhead than Prefect, Airflow, or Luigi, working instantly without complicated configuration.

![Taskinity Logo](./assets/taskinity-logo.svg)

## Mission

Our mission is to provide a simple yet powerful task orchestration tool that allows teams to focus on business logic rather than infrastructure management. We believe workflow automation should be accessible to everyone, regardless of team size or budget.

## Strategy

Taskinity achieves its mission through:

1. **Ease of use** - intuitive interface and minimal configuration
2. **Scalability** - from simple scripts to complex production workflows
3. **Flexibility** - easy integration with existing systems and tools
4. **Transparency** - full visibility of task status and execution history
5. **Reliability** - fault tolerance and automatic recovery mechanisms

## Navigation Menu

- [Documentation](./docs/documentation.md) - Complete technical documentation
- [Tutorial](./docs/tutorial.md) - Step-by-step introduction to Taskinity
- [Examples](./examples/README.md) - Ready-to-use flow examples
- [FAQ](./docs/faq.md) - Frequently asked questions
- [Troubleshooting](./docs/troubleshooting.md) - Help with solving problems

## Table of Contents

- [Advantages of Taskinity](#advantages-of-taskinity)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [DSL Specification](#dsl-specification)
- [Examples](#examples)
- [Flow Visualization](#flow-visualization)
- [Monitoring and Logs](#monitoring-and-logs)
- [Comparison with Other Frameworks](#comparison-with-other-frameworks)
- [Dashboard](#dashboard)
- [Notifications](#notifications)
- [Parallel Execution](#parallel-execution)
- [Flow Scheduling](#flow-scheduling)
- [Email Processing](#email-processing)
- [API Reference](#api-reference)
- [Extensions and Plugins](#extensions-and-plugins)

## Advantages of Taskinity

- **Simplicity** - minimal feature set, easy to understand and extend
- **Decorators** - intuitive way to define tasks and flows
- **DSL** - readable language for defining connections between tasks
- **Zero-config** - works immediately without complicated setup
- **Advanced monitoring** - automatic logging and execution tracking with metrics
- **Visualization** - interactive tools for flow visualization
- **Data validation** - built-in mechanisms for input and output data validation
- **Parallel execution** - automatic flow optimization for better performance
- **Reproducibility** - full execution history and ability to recreate flows
- **Modularity** - core functionality with optional extensions
- **Data processing** - built-in tools for various data sources
- **API integration** - easy connection to external services

## Quick Start

### Installation

Taskinity can be installed using pip or poetry:

```bash
# Installation with pip
pip install taskinity

# OR installation with poetry
poetry add taskinity

# Clone repository (optional for the latest development version)
git clone https://github.com/taskinity/python.git
cd taskinity

# Run example
python -m examples.basic_flow
```

### Basic Usage

```python
from taskinity import task, run_flow_from_dsl

# 1. Define tasks
@task(name="Fetch Data")
def fetch_data(url: str):
    # Implementation
    return data

@task(name="Process Data")
def process_data(data):
    # Implementation
    return processed_data

# 2. Define flow using DSL
flow_dsl = """
flow DataProcessing:
    description: "Data Processing Flow"
    fetch_data -> process_data
"""

# 3. Run the flow
results = run_flow_from_dsl(flow_dsl, {"url": "https://example.com/data"})
```

## DSL Specification

Taskinity uses a readable language for defining flows:

## Project Structure

Taskinity follows a modular architecture for better organization and extensibility:

### Core Module

The core module (`taskinity/core/`) contains the essential functionality:

- Task and flow decorators
- DSL parser and executor
- Flow management utilities
- Registry and execution tracking

### Extensions

Optional extensions enhance Taskinity with additional features:

- **Visualization** - Convert flows to Mermaid diagrams and export to SVG/PNG
- **Code Converter** - Convert existing Python code to Taskinity flows
- **Data Processors** - Tools for working with CSV, JSON, and databases
- **API Clients** - Clients for REST, GraphQL, and WebSocket APIs

### Examples

Taskinity includes a variety of examples in the `examples` directory:

- **Email Processing** - Process emails from IMAP servers with Docker configuration
- **Data Processing** - Process data from various sources with PostgreSQL integration
- **API Integration** - Connect to external APIs with a mock server for testing
- **Visualization** - Visualize flows with Mermaid and interactive diagrams
- **Parallel Tasks** - Optimize performance with parallel task execution

## DSL Specification

### Syntax Elements:

- **flow [FlowName]:** - Flow definition with name
- **description:** - Optional flow description
- **[source_task] -> [target_task]** - Definition of connection between tasks
- **[zadanie_źródłowe] -> [zadanie1, zadanie2]** - Połączenie jednego zadania z wieloma zadaniami

### Przykład:

```
flow EmailProcessing:
    description: "Przetwarzanie e-maili"
    fetch_emails -> classify_emails
    classify_emails -> process_urgent_emails
    classify_emails -> process_regular_emails
    process_urgent_emails -> send_responses
    process_regular_emails -> send_responses
```

## Examples

Taskinity includes a variety of examples in the `examples` directory. Each example is self-contained with its own README, configuration files, and Docker setup where applicable.

### Email Processing

```python
from taskinity import task, run_flow_from_dsl

@task(name="Fetch Emails")
def fetch_emails(server, username, password):
    # Implementation
    return ["Email 1", "Email 2"]

@task(name="Classify Emails")
def classify_emails(emails):
    # Implementation
    urgent = [e for e in emails if "URGENT" in e]
    regular = [e for e in emails if "URGENT" not in e]
    return {"urgent_emails": urgent, "regular_emails": regular}

@task(name="Process Urgent Emails")
def process_urgent_emails(urgent_emails):
    # Implementation
    return ["Response to urgent email" for _ in urgent_emails]

@task(name="Process Regular Emails")
def process_regular_emails(regular_emails):
    # Implementation
    return ["Response to regular email" for _ in regular_emails]

# Flow definition using DSL
email_dsl = """
flow EmailProcessing:
    description: "Email Processing Flow"
    fetch_emails -> classify_emails
    classify_emails -> process_urgent_emails
    classify_emails -> process_regular_emails
"""

# Run the flow
results = run_flow_from_dsl(email_dsl, {
    "server": "imap.example.com",
    "username": "user@example.com",
    "password": "password123"
})
```

### Data Analysis with Validation

```python
from taskinity import task, run_flow_from_dsl

def validate_input_data(data):
    if not isinstance(data, list):
        raise ValueError("Input data must be a list")
    if len(data) == 0:
        raise ValueError("Data list cannot be empty")

def validate_output_data(result):
    if not isinstance(result, dict):
        raise ValueError("Result must be a dictionary")
    if "summary" not in result or "average" not in result:
        raise ValueError("Result must contain 'summary' and 'average' keys")

@task(name="Fetch Data")
def fetch_data():
    # Implementation
    return [1, 2, 3, 4, 5]

@task(name="Analyze Data", validate_input=validate_input_data, validate_output=validate_output_data)
def analyze_data(data):
    # Implementation
    return {"summary": sum(data), "average": sum(data) / len(data)}

# Flow definition using DSL
data_dsl = """
flow DataAnalysis:
    description: "Data Analysis with Validation"
    fetch_data -> analyze_data
"""

# Run the flow
results = run_flow_from_dsl(data_dsl, {})
```

## Wizualizacja przepływów

Taskinity zawiera proste narzędzia do wizualizacji przepływów:

```python
# Wizualizacja definicji DSL
python visualize_flow.py dsl --file email_processing.dsl --output flow_diagram.png

# Wizualizacja historii wykonania przepływu
python visualize_flow.py flow [flow_id] --output execution_diagram.png

# Wyświetlenie listy dostępnych przepływów
python visualize_flow.py list --flows
```

## Monitoring and Logs

Taskinity automatycznie zapisuje logi wykonania przepływów w katalogu `logs/`. Można je łatwo przeglądać za pomocą standardowych narzędzi:

```python
# Wyświetlenie logów dla konkretnego przepływu
import json
from pathlib import Path

def view_flow_logs(flow_id):
    flow_file = Path("flows") / f"{flow_id}.json"
    if not flow_file.exists():
        print(f"Nie znaleziono przepływu o ID: {flow_id}")
        return
    
    with open(flow_file, "r") as f:
        flow_data = json.load(f)
    
    print(f"Przepływ: {flow_data['name']} (Status: {flow_data['status']})")
    print(f"Czas rozpoczęcia: {flow_data['start_time']}")
    print(f"Czas zakończenia: {flow_data.get('end_time', 'N/A')}")
    print(f"Czas trwania: {flow_data.get('duration', 'N/A')} sekund")
    
    if 'error' in flow_data:
        print(f"Błąd: {flow_data['error']}")
    
    print("\nZadania:")
    for task_id in flow_data.get('tasks', []):
        task_file = Path("flows") / f"{task_id}.json"
        if task_file.exists():
            with open(task_file, "r") as f:
                task_data = json.load(f)
            print(f"  - {task_data['name']} (Status: {task_data['status']}, Czas: {task_data.get('duration', 'N/A')} sekund)")
```

## Comparison with Other Frameworks

### Tabela Porównawcza Frameworków

| Kryterium               | taskinity                  | Prefect                   | Airflow                  | Luigi                     | Bonobo                   | Kedro                    | Mara                     |
|-------------------------|--------------------------|---------------------------|--------------------------|---------------------------|--------------------------|--------------------------|--------------------------|  
| **Typ Projektu**        | Lekkie przepływy          | Złożone orchestracje      | Złożone ETL              | Proste ETL                | ETL strumieniowe         | Pipeline'y danych        | Proste ETL               |
| **Składnia**            | DSL + dekoratory          | Dekoratory `@flow/@task`  | Klasy z `DAG`            | Klasy z `run()`           | Funkcje + graf           | Węzły i pipeline'y       | Funkcje + dekoratory     |
| **Zależności**          | Brak                      | `prefect>=2.0`            | `apache-airflow`         | `luigi`                   | `bonobo`                 | `kedro`                  | `mara`                   |
| **Obserwowalność**      | Podstawowe logi + UI      | Grafana/Prometheus        | Wbudowany UI             | Logi tekstowe             | Konsola                  | Wbudowany dashboard      | Prosty interfejs webowy  |
| **Walidacja Danych**    | Własne funkcje            | Typy Pydantic             | Brak                     | Brak                      | Brak                     | Schematy datasetów       | Brak                     |
| **Równoległość**        | Wątki (przyszłe)          | Wątki/Procesy             | Executor                 | Sekwencyjne               | Wątki                    | Równoległe wykonanie     | Sekwencyjne              |
| **Integracje**          | Brak (rozszerzalne)       | 100+ konektorów           | 200+ konektorów          | Ograniczone               | CSV/JSON/SQL             | Wsparcie MLflow          | PostgreSQL/Redshift      |
| **UI/Dashboard**        | Prosty, lekki dashboard   | Prefect Cloud/UI          | Airflow UI               | Brak                      | Brak                     | Kedro-Viz                | Mara UI                  |
| **Skalowalność**        | Lokalna                   | Klastry Dask/Kubernetes   | Celery/Kubernetes        | Apache Hadoop             | Lokalna                  | Lokalna                  | Lokalna                  |
| **Czas Konfiguracji**   | < 1 minuta                | 15-30 minut               | 30-60 minut              | 5-10 minut                | 2-5 minut                | 10-20 minut              | 5-10 minut               |
| **Rozmiar kodu**        | < 1000 linii              | > 100,000 linii           | > 500,000 linii          | > 50,000 linii            | ~15,000 linii            | > 30,000 linii           | ~10,000 linii            |
| **Krzywa uczenia**      | Bardzo płaska            | Umiarkowana               | Stroma                   | Umiarkowana               | Płaska                   | Umiarkowana              | Płaska                   |

### Implementacje Przykładowe

#### 1. taskinity: Automatyzacja Klasyfikacji Emaili
```python
from flow_dsl import task, run_flow_from_dsl

@task(name="Pobierz maile")
def fetch_emails(server: str) -> list:
    # Implementacja pobierania
    return emails

@task(name="Klasyfikuj")
def classify(emails: list) -> dict:
    # Klasyfikacja maili
    return {"urgent": [...], "regular": [...]}

flow = """
flow EmailFlow:
    fetch_emails -> classify
"""

run_flow_from_dsl(flow, {"server": "imap.example.com"})
```

#### 2. Bonobo: Przetwarzanie Strumieniowe
```python
import bonobo

def fetch_emails():
    # Generator zwracający maile jeden po drugim
    yield from imap_fetch()

def classify(email):
    # Przetwarzanie każdego rekordu
    return {**email, "label": model(email['body'])}

graph = bonobo.Graph()
graph.add_chain(fetch_emails, classify, bonobo.JsonWriter('output.json'))

bonobo.run(graph)
```

#### 3. Kedro: Strukturyzowany Pipeline Danych
```python
# nodes.py
def preprocess_emails(emails: pd.DataFrame) -> pd.DataFrame:
    emails['label'] = emails['body'].apply(lambda x: classify(x))
    return emails

# pipeline.py
from kedro.pipeline import node, Pipeline

pipeline = Pipeline([
    node(
        func=preprocess_emails,
        inputs="raw_emails",
        outputs="classified_emails",
        name="classification_node"
    )
])

# uruchomienie
kedro run
```

### Kiedy używać taskinity?

- **Małe i średnie projekty**: Gdy potrzebujesz szybko zaimplementować przepływ pracy bez nadmiernej złożoności
- **Prototypowanie**: Gdy chcesz szybko przetestować koncepcję przepływu bez konfiguracji infrastruktury
- **Czytelność**: Gdy zależy Ci na czytelnym DSL, który mogą zrozumieć również osoby nietechniczne
- **Minimalizm**: Gdy nie potrzebujesz zaawansowanych funkcji jak planowanie czy rozproszone wykonanie
- **Natychmiastowe użycie**: Gdy chcesz zacząć bez instalacji i konfiguracji dodatkowych komponentów

### Kiedy używać innych frameworków?

- **Prefect**: Gdy potrzebujesz zaawansowanego monitorowania, skalowania i integracji z chmurą
- **Airflow**: Gdy potrzebujesz zaawansowanego planowania, wielu integracji i masz duży zespół DevOps
- **Luigi**: Gdy potrzebujesz prostszego frameworka niż Airflow, ale bardziej rozbudowanego niż taskinity
- **Bonobo**: Gdy potrzebujesz przetwarzania strumieniowego i prostych transformacji ETL
- **Kedro**: Gdy pracujesz nad projektami data science i potrzebujesz struktury projektu
- **Mara**: Gdy potrzebujesz prostego ETL z interfejsem webowym

### Rekomendowany Stack Technologiczny

#### Dla Małych Zespołów (do 10 użytkowników):
- **Orchestracja**: taskinity (prostota) lub Mara (ETL + UI)
- **Przetwarzanie**: Pandas/NumPy
- **ML**: Scikit-learn/Hugging Face Transformers
- **Dashboard**: Streamlit (szybki prototyp)

#### Dla Średnich Projektów (10-100 użytkowników):
- **Orchestracja**: Prefect (monitoring) lub Kedro (struktura projektu)
- **Przetwarzanie**: Dask dla równoległości
- **ML**: MLflow/Kubeflow
- **Dashboard**: Plotly Dash/Grafana

## Dashboardy i Wizualizacja

taskinity oferuje dwa rodzaje dashboardów do monitorowania przepływów:

### 1. Mini Dashboard

Prosty, lekki dashboard z widokiem historii logów i możliwością szybkiego podglądu diagramów:

```bash
python mini_dashboard.py
```

**Funkcje Mini Dashboardu:**
- Historia przepływów z filtrowaniem (Wszystkie/Ukończone/Błędy/Uruchomione)
- Pomniejszone diagramy SVG (90% oryginalnej wielkości)
- Możliwość edycji diagramu bezpośrednio w interfejsie z kolorowaniem składni
- Domyślnie otwarte logi dla każdego przepływu z kolorowaniem składni
- Szczegóły zadań w przepływie
- Powiadomienia o statusie przepływów (email/Slack)
- Równoległe wykonanie niezależnych zadań
- Planowanie wykonania przepływów

![Mini Dashboard](https://via.placeholder.com/600x300/0078D4/FFFFFF?text=Mini+Dashboard)

### 2. Pełny Dashboard

Rozbudowany dashboard z pełną funkcjonalnością:

```bash
python simple_dashboard.py
```

**Funkcje Pełnego Dashboardu:**
- Przeglądanie definicji DSL
- Zaawansowana wizualizacja przepływów
- Historia wykonania przepływów
- Przeglądanie logów
- Uruchamianie przepływów
- Eksport diagramów do SVG

### 3. Wizualizacja w Linii Komend

Możliwość generowania diagramów bez uruchamiania dashboardu:

```bash
# Wizualizacja definicji DSL
python flow_visualizer.py dsl --file dsl_definitions/email_processing.dsl --output diagram.html

# Wizualizacja historii przepływu
python flow_visualizer.py flow [flow_id] --output flow_diagram.html

# Generowanie diagramu ASCII
python flow_visualizer.py dsl --file dsl_definitions/email_processing.dsl --ascii
```

**Przykład diagramu ASCII:**
```
=== EmailProcessing ===

[fetch_emails]
[classify_emails]
[process_urgent_emails]
[process_regular_emails]
[send_responses]

Połączenia:
fetch_emails --> classify_emails
classify_emails --> process_urgent_emails
classify_emails --> process_regular_emails
process_urgent_emails --> send_responses
process_regular_emails --> send_responses
```

## Powiadomienia

taskinity oferuje system powiadomień o statusie przepływów przez email i Slack:

### Konfiguracja Powiadomień

```bash
# Edycja konfiguracji powiadomień
python -c "from notification_service import load_config, save_config; config = load_config(); config['enabled'] = True; save_config(config)"
```

Lub poprzez API w mini dashboardzie:

```
POST /api/notifications/config
```

**Funkcje Powiadomień:**
- Powiadomienia o rozpoczęciu przepływu
- Powiadomienia o zakończeniu przepływu
- Powiadomienia o błędach w przepływie
- Szczegółowe informacje o zadaniach
- Wsparcie dla email (SMTP) i Slack (Webhook)

## Równoległe Wykonanie

taskinity umożliwia równoległe wykonanie niezależnych zadań w przepływie:

```python
# Uruchomienie przepływu z równoległym wykonaniem
from parallel_executor import run_parallel_flow_from_dsl

result = run_parallel_flow_from_dsl(dsl_content, input_data)
```

Lub poprzez API w mini dashboardzie:

```
POST /api/run
{
  "dsl": "...",
  "use_parallel": true
}
```

**Zalety Równoległego Wykonania:**
- Szybsze wykonanie przepływów z niezależnymi zadaniami
- Automatyczne wykrywanie zależności między zadaniami
- Optymalne wykorzystanie dostępnych zasobów (CPU)
- Pełna kompatybilność z istniejącymi definicjami DSL



## Flow Scheduling

Taskinity allows scheduling automatic flow execution:

```bash
# Start the scheduler
python flow_scheduler.py start

# Create a schedule (every 60 minutes)
python flow_scheduler.py create dsl_definitions/email_processing.dsl 60

# List all schedules
python flow_scheduler.py list

# Manually run a schedule
python flow_scheduler.py run [schedule_id]

# Delete a schedule
python flow_scheduler.py delete [schedule_id]
```

Or through the API in the mini dashboard:

```
GET /api/schedules
POST /api/schedules
PUT /api/schedules/{schedule_id}
DELETE /api/schedules/{schedule_id}
POST /api/schedules/{schedule_id}/run
POST /api/scheduler/start
POST /api/scheduler/stop
```

**Schedule Types:**
- Interval (every X minutes)
- Daily (at a specific time)
- Weekly (on a specific day of the week)
- Monthly (on a specific day of the month)

## API Reference

### Decorators

#### `@task`

```python
@task(name=None, description=None, validate_input=None, validate_output=None)
def my_task():
    pass
```

- **name**: Optional task name (default: function name)
- **description**: Optional task description
- **validate_input**: Optional function for input data validation
- **validate_output**: Optional function for output data validation

#### `@flow`

```python
@flow(name=None, description=None)
def my_flow():
    pass
```

- **name**: Optional flow name (default: function name)
- **description**: Optional flow description

### Functions

#### `run_flow_from_dsl`

```python
run_flow_from_dsl(dsl_text, input_data=None)
```

- **dsl_text**: DSL text defining the flow
- **input_data**: Optional input data for the flow

#### `parse_dsl`

```python
parse_dsl(dsl_text)
```

- **dsl_text**: DSL text to parse

#### `save_dsl`

```python
save_dsl(dsl_text, filename)
```

- **dsl_text**: DSL text to save
- **filename**: Filename

#### `load_dsl`

```python
load_dsl(filename)
```

- **filename**: DSL filename to load

#### `list_flows`

```python
list_flows()
```

Returns a list of all executed flows.

## Extensions and Plugins

Taskinity follows a modular architecture where core functionality can be extended with plugins. The following extensions are available:

### Visualization Extensions

```python
from taskinity.extensions.mermaid_converter import convert_to_mermaid, export_as_svg

# Convert flow to Mermaid diagram
mermaid_code = convert_to_mermaid(flow_dsl)

# Export to SVG
svg_file = export_as_svg(mermaid_code, "flow_diagram.svg")
```

### Code Converter

```python
from taskinity.extensions.code_converter import convert_code_to_taskinity

# Convert existing Python code to Taskinity flow
dsl_text = convert_code_to_taskinity("path/to/script.py", "output_flow.dsl")
```

### Data Processors

```python
from taskinity.data_processors import CSVProcessor, JSONProcessor, DatabaseProcessor

# Process CSV data
csv_processor = CSVProcessor()
data = csv_processor.read("data.csv")
transformed_data = csv_processor.transform(data, lambda x: x * 2)
csv_processor.write(transformed_data, "output.csv")
```

### API Clients

```python
from taskinity.api_client import RESTClient, GraphQLClient

# Use REST client
rest_client = RESTClient("https://api.example.com")
response = rest_client.get("users")

# Use GraphQL client
graphql_client = GraphQLClient("https://api.example.com/graphql")
response = graphql_client.query("""
    query {
        users {
            id
            name
        }
    }
""")
```

### Future Extensions

1. **Web Dashboard** - interactive visualization of flows and their status
2. **Type Validation** - automatic validation of input/output data types
3. **Error Handling** - retry mechanisms and exception handling
4. **Persistence** - saving flow state in a database
5. **REST API** - API for managing flows

## License

[Apache License](LICENSE)
