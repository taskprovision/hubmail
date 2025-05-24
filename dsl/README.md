# Taskinity - Inteligentny Framework do Orkiestracji Zadań

Taskinity to nowoczesny framework do definiowania, zarządzania i monitorowania przepływów zadań za pomocą intuicyjnego języka DSL i dekoratorów Python. Zaprojektowany z myślą o prostocie i wydajności, Taskinity oferuje znacznie mniejszy narzut niż Prefect, Airflow czy Luigi, działając natychmiast bez skomplikowanej konfiguracji.

![Taskinity Logo](./assets/taskinity-logo.svg)

## Misja

Naszą misją jest dostarczenie prostego, ale potężnego narzędzia do orkiestracji zadań, które pozwala zespołom skupić się na logice biznesowej, a nie na zarządzaniu infrastrukturą. Wierzymy, że automatyzacja przepływów pracy powinna być dostępna dla wszystkich, niezależnie od wielkości zespołu czy budżetu.

## Strategia

Taskinity realizuje swoją misję poprzez:

1. **Prostotę użycia** - intuicyjny interfejs i minimalna konfiguracja
2. **Skalowalność** - od prostych skryptów po złożone przepływy produkcyjne
3. **Elastyczność** - łatwa integracja z istniejącymi systemami i narzędziami
4. **Transparentność** - pełna widoczność stanu i historii wykonania zadań
5. **Niezawodność** - odporność na błędy i mechanizmy automatycznego odzyskiwania

## Menu Nawigacyjne

- [Dokumentacja](./docs/dokumentacja.md) - Pełna dokumentacja techniczna
- [Samouczek](./docs/samouczek.md) - Krok po kroku wprowadzenie do Taskinity
- [Przykłady](./docs/przyklady.md) - Gotowe przykłady przepływów
- [FAQ](./docs/faq.md) - Najczęściej zadawane pytania
- [Rozwiązywanie problemów](./docs/troubleshooting.md) - Pomoc w rozwiązywaniu problemów

## Spis treści

- [Zalety Taskinity](#zalety-taskinity)
- [Szybki start](#szybki-start)
- [Specyfikacja DSL](#specyfikacja-dsl)
- [Przykłady użycia](#przykłady-użycia)
- [Wizualizacja przepływów](#wizualizacja-przepływów)
- [Monitorowanie i logi](#monitorowanie-i-logi)
- [Porównanie z innymi frameworkami](#porównanie-z-innymi-frameworkami)
- [Dashboard](#dashboard)
- [Powiadomienia](#powiadomienia)
- [Równoległe Wykonanie](#równoległe-wykonanie)
- [Planowanie Przepływów](#planowanie-przepływów)
- [Przetwarzanie Email](#przetwarzanie-email)
- [API Reference](#api-reference)
- [Rozszerzenia i ulepszenia](#rozszerzenia-i-ulepszenia)

## Zalety Taskinity

- **Prostota** - minimalny zestaw funkcji, łatwy do zrozumienia i rozszerzenia
- **Dekoratory** - intuicyjny sposób definiowania zadań i przepływów
- **DSL** - czytelny język do definiowania połączeń między zadaniami
- **Zero-config** - działa natychmiast, bez skomplikowanej konfiguracji
- **Zaawansowany monitoring** - automatyczne logowanie i śledzenie wykonania z metrykami
- **Wizualizacja** - interaktywne narzędzia do wizualizacji przepływów
- **Walidacja danych** - wbudowane mechanizmy walidacji danych wejściowych i wyjściowych
- **Równoległe wykonanie** - automatyczna optymalizacja przepływów dla lepszej wydajności
- **Odtwarzalność** - pełna historia wykonania i możliwość odtworzenia przepływów

## Szybki start

### Instalacja

Taskinity można zainstalować za pomocą pip lub poetry:

```bash
# Instalacja przez pip
pip install taskinity

# LUB instalacja przez poetry
poetry add taskinity

# Klonowanie repozytorium (opcjonalnie dla najnowszej wersji rozwojowej)
git clone https://github.com/taskprovision/taskinity.git
cd taskinity

# Uruchomienie przykładu
python -m examples.basic_flow
```

### Podstawowe użycie

```python
from taskinity import task, run_flow_from_dsl

# 1. Definiowanie zadań
@task(name="Pobieranie danych")
def fetch_data(url: str):
    # Implementacja
    return data

@task(name="Przetwarzanie danych")
def process_data(data):
    # Implementacja
    return processed_data

# 2. Definiowanie przepływu DSL
flow_dsl = """
flow DataProcessing:
    description: "Przetwarzanie danych"
    fetch_data -> process_data
"""

# 3. Uruchamianie przepływu
results = run_flow_from_dsl(flow_dsl, {"url": "https://example.com/data"})
```

## Specyfikacja DSL

Taskinity używa czytelnego języka do definiowania przepływów:

```
flow [NazwaPrzepływu]:
    description: "[Opis przepływu]"
    [zadanie_źródłowe] -> [zadanie_docelowe]
    [zadanie_źródłowe] -> [zadanie_docelowe1, zadanie_docelowe2]
    [zadanie_źródłowe] -> [zadanie_docelowe]
```

### Elementy składni:

- **flow [NazwaPrzepływu]:** - Definicja przepływu z nazwą
- **description:** - Opcjonalny opis przepływu
- **[zadanie_źródłowe] -> [zadanie_docelowe]** - Definicja połączenia między zadaniami
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

## Przykłady użycia

### Przykład 1: Przetwarzanie e-maili

```python
from flow_dsl import task, flow, run_flow_from_dsl

@task(name="Pobieranie e-maili")
def fetch_emails(server, username, password):
    # Implementacja
    return emails

@task(name="Klasyfikacja e-maili")
def classify_emails(emails):
    urgent = [email for email in emails if email.get("urgent", False)]
    regular = [email for email in emails if not email.get("urgent", False)]
    return {"urgent_emails": urgent, "regular_emails": regular}

@task(name="Przetwarzanie pilnych e-maili")
def process_urgent_emails(urgent_emails):
    # Implementacja
    return ["Odpowiedź na pilny e-mail" for _ in urgent_emails]

@task(name="Przetwarzanie zwykłych e-maili")
def process_regular_emails(regular_emails):
    # Implementacja
    return ["Odpowiedź na zwykły e-mail" for _ in regular_emails]

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
    "username": "info@softreck.dev",
    "password": "password123"
})
```

### Przykład 2: Przetwarzanie danych z walidacją

```python
from flow_dsl import task, run_flow_from_dsl

# Funkcje walidacji
def validate_input_data(data):
    if not isinstance(data, list):
        raise ValueError("Dane wejściowe muszą być listą")
    if len(data) == 0:
        raise ValueError("Lista danych nie może być pusta")

def validate_output_data(result):
    if not isinstance(result, dict):
        raise ValueError("Wynik musi być słownikiem")
    if "summary" not in result:
        raise ValueError("Wynik musi zawierać klucz 'summary'")

@task(name="Pobieranie danych", validate_output=validate_input_data)
def fetch_data():
    # Implementacja
    return [1, 2, 3, 4, 5]

@task(name="Analiza danych", validate_input=validate_input_data, validate_output=validate_output_data)
def analyze_data(data):
    # Implementacja
    return {"summary": sum(data), "average": sum(data) / len(data)}

# Definicja przepływu DSL
data_dsl = """
flow DataAnalysis:
    description: "Analiza danych z walidacją"
    fetch_data -> analyze_data
"""

# Uruchomienie przepływu
results = run_flow_from_dsl(data_dsl, {})
```

## Wizualizacja przepływów

taskinity zawiera proste narzędzia do wizualizacji przepływów:

```python
# Wizualizacja definicji DSL
python visualize_flow.py dsl --file email_processing.dsl --output flow_diagram.png

# Wizualizacja historii wykonania przepływu
python visualize_flow.py flow [flow_id] --output execution_diagram.png

# Wyświetlenie listy dostępnych przepływów
python visualize_flow.py list --flows
```

## Monitorowanie i logi

taskinity automatycznie zapisuje logi wykonania przepływów w katalogu `logs/`. Można je łatwo przeglądać za pomocą standardowych narzędzi:

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

## Analiza Porównawcza Frameworków Orchestracji w Pythonie

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

## Planowanie Przepływów

taskinity pozwala na planowanie automatycznego wykonania przepływów:

```bash
# Uruchomienie planera
python flow_scheduler.py start

# Utworzenie harmonogramu (co 60 minut)
python flow_scheduler.py create dsl_definitions/email_processing.dsl 60

# Lista harmonogramów
python flow_scheduler.py list

# Ręczne uruchomienie harmonogramu
python flow_scheduler.py run [schedule_id]

# Usunięcie harmonogramu
python flow_scheduler.py delete [schedule_id]
```

Lub poprzez API w mini dashboardzie:

```
GET /api/schedules
POST /api/schedules
PUT /api/schedules/{schedule_id}
DELETE /api/schedules/{schedule_id}
POST /api/schedules/{schedule_id}/run
POST /api/scheduler/start
POST /api/scheduler/stop
```

**Typy Harmonogramów:**
- Interwałowy (co X minut)
- Dzienny (o określonej godzinie)
- Tygodniowy (w określony dzień tygodnia)
- Miesięczny (w określony dzień miesiąca)

## API Reference

### Dekoratory

#### `@task`

```python
@task(name=None, description=None, validate_input=None, validate_output=None)
def my_task():
    pass
```

- **name**: Opcjonalna nazwa zadania (domyślnie: nazwa funkcji)
- **description**: Opcjonalny opis zadania
- **validate_input**: Opcjonalna funkcja do walidacji danych wejściowych
- **validate_output**: Opcjonalna funkcja do walidacji danych wyjściowych

#### `@flow`

```python
@flow(name=None, description=None)
def my_flow():
    pass
```

- **name**: Opcjonalna nazwa przepływu (domyślnie: nazwa funkcji)
- **description**: Opcjonalny opis przepływu

### Funkcje

#### `run_flow_from_dsl`

```python
run_flow_from_dsl(dsl_text, input_data=None)
```

- **dsl_text**: Tekst DSL definiujący przepływ
- **input_data**: Opcjonalne dane wejściowe dla przepływu

#### `parse_dsl`

```python
parse_dsl(dsl_text)
```

- **dsl_text**: Tekst DSL do sparsowania

#### `save_dsl`

```python
save_dsl(dsl_text, filename)
```

- **dsl_text**: Tekst DSL do zapisania
- **filename**: Nazwa pliku

#### `load_dsl`

```python
load_dsl(filename)
```

- **filename**: Nazwa pliku DSL do wczytania

#### `list_flows`

```python
list_flows()
```

Zwraca listę wszystkich wykonanych przepływów.

## Rozszerzenia i ulepszenia

1. **Dashboard webowy** - interaktywna wizualizacja przepływów i ich statusu
2. **Walidacja typów** - automatyczna walidacja typów danych wejściowych/wyjściowych
3. **Równoległe wykonanie** - możliwość równoległego wykonania niezależnych zadań
4. **Obsługa błędów** - mechanizmy ponownych prób i obsługi wyjątków
5. **Zaplanowane wykonanie** - mechanizm planowania wykonania przepływów
6. **Integracje** - dodanie konectorów do popularnych systemów
7. **Persystencja** - zapisywanie stanu przepływów w bazie danych
8. **API REST** - udostępnienie API do zarządzania przepływami

## Licencja

[LICENSE](LICENSE)
