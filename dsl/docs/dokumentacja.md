# Dokumentacja Techniczna taskinity

## Spis treści

- [Wprowadzenie](#wprowadzenie)
- [Architektura](#architektura)
- [Instalacja](#instalacja)
- [Podstawowe komponenty](#podstawowe-komponenty)
- [Zaawansowane funkcje](#zaawansowane-funkcje)
- [API Reference](#api-reference)
- [Integracje](#integracje)
- [Rozwiązywanie problemów](#rozwiązywanie-problemów)
- [FAQ](#faq)

## Wprowadzenie

taskinity to lekki framework do definiowania i uruchamiania przepływów zadań za pomocą prostego języka DSL i dekoratorów Python. Został zaprojektowany z myślą o prostocie i elastyczności, umożliwiając szybkie tworzenie i zarządzanie przepływami zadań bez konieczności konfiguracji skomplikowanej infrastruktury.

### Główne cechy

- **Prosty język DSL** - intuicyjny sposób definiowania przepływów
- **Dekoratory Python** - łatwe definiowanie zadań
- **Minimalne zależności** - działa natychmiast bez skomplikowanej konfiguracji
- **Wizualizacja** - automatyczne generowanie diagramów przepływów
- **Monitorowanie** - śledzenie wykonania i logowanie
- **Dashboard** - interfejs webowy do zarządzania przepływami
- **Powiadomienia** - email i Slack
- **Równoległe wykonanie** - optymalizacja wydajności
- **Planowanie** - automatyczne uruchamianie przepływów

## Architektura

taskinity składa się z następujących głównych komponentów:

1. **Parser DSL** - odpowiedzialny za parsowanie definicji przepływów
2. **Silnik wykonawczy** - zarządza wykonaniem zadań i przepływów
3. **System logowania** - rejestruje zdarzenia i błędy
4. **Wizualizator** - generuje diagramy przepływów
5. **Dashboard** - interfejs webowy
6. **Serwis powiadomień** - wysyła powiadomienia
7. **Równoległy wykonawca** - zarządza równoległym wykonaniem zadań
8. **Planer** - zarządza harmonogramami przepływów
9. **Procesor email** - analizuje i przetwarza emaile

### Diagram architektury

```
+----------------+     +----------------+     +----------------+
|                |     |                |     |                |
|  Parser DSL    |---->|  Silnik        |---->|  System        |
|                |     |  wykonawczy    |     |  logowania     |
+----------------+     +----------------+     +----------------+
                              |
                              v
+----------------+     +----------------+     +----------------+
|                |     |                |     |                |
|  Wizualizator  |<----|  Dashboard     |---->|  Serwis        |
|                |     |                |     |  powiadomień   |
+----------------+     +----------------+     +----------------+
                              |
                              v
+----------------+     +----------------+     +----------------+
|                |     |                |     |                |
|  Równoległy    |<----|  Planer        |---->|  Procesor      |
|  wykonawca     |     |                |     |  email         |
+----------------+     +----------------+     +----------------+
```

## Instalacja

taskinity nie wymaga skomplikowanej instalacji. Wystarczy skopiować pliki do projektu lub sklonować repozytorium:

```bash
# Klonowanie repozytorium
git clone https://github.com/taskinity/hubmail.git
cd hubmail/dsl

# Instalacja zależności
pip install -r requirements.txt
```

### Wymagania systemowe

- Python 3.7+
- Zależności wymienione w `requirements.txt`

## Podstawowe komponenty

### Dekorator `@task`

Dekorator `@task` służy do definiowania zadań w przepływie:

```python
from flow_dsl import task

@task(name="Pobieranie danych", description="Pobiera dane z API")
def fetch_data(url: str):
    # Implementacja
    return data
```

Parametry:
- `name` (opcjonalny) - nazwa zadania (domyślnie: nazwa funkcji)
- `description` (opcjonalny) - opis zadania
- `validate_input` (opcjonalny) - funkcja do walidacji danych wejściowych
- `validate_output` (opcjonalny) - funkcja do walidacji danych wyjściowych

### Język DSL

taskinity używa prostego języka do definiowania przepływów:

```
flow [NazwaPrzepływu]:
    description: "[Opis przepływu]"
    [zadanie_źródłowe] -> [zadanie_docelowe]
    [zadanie_źródłowe] -> [zadanie_docelowe1, zadanie_docelowe2]
```

Elementy składni:
- `flow [NazwaPrzepływu]:` - definicja przepływu z nazwą
- `description:` - opcjonalny opis przepływu
- `[zadanie_źródłowe] -> [zadanie_docelowe]` - definicja połączenia między zadaniami
- `[zadanie_źródłowe] -> [zadanie1, zadanie2]` - połączenie jednego zadania z wieloma zadaniami

### Funkcja `run_flow_from_dsl`

Funkcja `run_flow_from_dsl` służy do uruchamiania przepływów zdefiniowanych w DSL:

```python
from flow_dsl import run_flow_from_dsl

flow_dsl = """
flow DataProcessing:
    description: "Przetwarzanie danych"
    fetch_data -> process_data
"""

results = run_flow_from_dsl(flow_dsl, {"url": "https://example.com/data"})
```

Parametry:
- `dsl_text` - tekst DSL definiujący przepływ
- `input_data` (opcjonalny) - dane wejściowe dla przepływu

## Zaawansowane funkcje

### Wizualizacja przepływów

taskinity zawiera narzędzia do wizualizacji przepływów:

```python
from flow_visualizer import visualize_dsl, visualize_flow

# Wizualizacja definicji DSL
visualize_dsl(dsl_text, output_file="flow_diagram.png")

# Wizualizacja historii wykonania przepływu
visualize_flow(flow_id, output_file="execution_diagram.png")
```

### Dashboard

taskinity zawiera dwa dashboardy do zarządzania przepływami:

1. **Mini Dashboard** - prosty dashboard z podstawowymi funkcjami:

```bash
python mini_dashboard.py
```

2. **Pełny Dashboard** - rozbudowany dashboard z pełną funkcjonalnością:

```bash
python simple_dashboard.py
```

### Powiadomienia

taskinity umożliwia wysyłanie powiadomień o statusie przepływów:

```python
from notification_service import send_email_notification, send_slack_notification

# Wysyłanie powiadomienia email
send_email_notification("Przepływ zakończony", "Przepływ XYZ zakończony pomyślnie.")

# Wysyłanie powiadomienia Slack
send_slack_notification("Przepływ zakończony", "Przepływ XYZ zakończony pomyślnie.")
```

### Równoległe wykonanie

taskinity umożliwia równoległe wykonanie niezależnych zadań w przepływie:

```python
from parallel_executor import run_parallel_flow_from_dsl

result = run_parallel_flow_from_dsl(dsl_content, input_data)
```

### Planowanie przepływów

taskinity pozwala na planowanie automatycznego wykonania przepływów:

```python
from flow_scheduler import Scheduler

# Utworzenie planera
scheduler = Scheduler()

# Dodanie harmonogramu (co 60 minut)
scheduler.add_schedule("dsl_definitions/email_processing.dsl", interval=60)

# Uruchomienie planera
scheduler.start()
```

### Przetwarzanie email

taskinity zawiera moduł do przetwarzania emaili:

```python
from email_pipeline import EmailProcessor

# Utworzenie procesora emaili
processor = EmailProcessor()

# Przetwarzanie emaili
processor.process_emails()
```

## API Reference

### Moduł `flow_dsl`

#### Dekoratory

- `@task(name=None, description=None, validate_input=None, validate_output=None)`
- `@flow(name=None, description=None)`

#### Funkcje

- `run_flow_from_dsl(dsl_text, input_data=None)`
- `parse_dsl(dsl_text)`
- `save_dsl(dsl_text, filename)`
- `load_dsl(filename)`
- `list_flows()`

### Moduł `flow_visualizer`

- `visualize_dsl(dsl_text, output_file=None, format="png")`
- `visualize_flow(flow_id, output_file=None, format="png")`
- `generate_mermaid(dsl_text)`
- `generate_flow_mermaid(flow_id)`

### Moduł `notification_service`

- `send_email_notification(subject, message, config=None)`
- `send_slack_notification(title, message, config=None)`
- `load_config()`
- `save_config(config)`

### Moduł `parallel_executor`

- `run_parallel_flow_from_dsl(dsl_text, input_data=None, max_workers=None)`
- `execute_parallel_tasks(tasks, dependencies, results, max_workers=None)`

### Moduł `flow_scheduler`

- `Scheduler.add_schedule(dsl_file, interval=None, daily=None, weekly=None, monthly=None)`
- `Scheduler.remove_schedule(schedule_id)`
- `Scheduler.start()`
- `Scheduler.stop()`
- `Scheduler.list_schedules()`

### Moduł `email_pipeline`

- `EmailProcessor.process_emails()`
- `EmailProcessor.fetch_emails()`
- `EmailProcessor.send_auto_reply(email_data, template_key)`
- `EmailProcessor.trigger_flow(email_data)`

## Integracje

taskinity może być łatwo zintegrowany z innymi narzędziami i systemami:

### Integracja z systemami powiadomień

- **Email** - wysyłanie powiadomień email przez SMTP
- **Slack** - wysyłanie powiadomień przez webhooks Slack

### Integracja z systemami monitorowania

- **Logi** - zapisywanie logów do plików
- **Metryki** - zbieranie metryk wykonania

### Integracja z systemami przetwarzania danych

- **Pandas** - przetwarzanie danych tabelarycznych
- **NumPy** - operacje na macierzach i tablicach
- **Scikit-learn** - modele uczenia maszynowego

## Rozwiązywanie problemów

### Typowe problemy i rozwiązania

1. **Problem: Zadanie nie jest wykonywane**
   - Sprawdź, czy zadanie jest poprawnie zdefiniowane w DSL
   - Sprawdź, czy zadanie jest poprawnie połączone z innymi zadaniami
   - Sprawdź logi wykonania

2. **Problem: Błąd parsowania DSL**
   - Sprawdź składnię DSL
   - Sprawdź wcięcia i spacje
   - Sprawdź, czy wszystkie zadania są zdefiniowane

3. **Problem: Powiadomienia nie są wysyłane**
   - Sprawdź konfigurację SMTP/Slack
   - Sprawdź, czy powiadomienia są włączone
   - Sprawdź logi serwisu powiadomień

4. **Problem: Dashboard nie działa**
   - Sprawdź, czy serwer jest uruchomiony
   - Sprawdź, czy port nie jest zajęty
   - Sprawdź logi serwera

### Logi i debugowanie

taskinity zapisuje logi w katalogu `logs/`:

- `flow_dsl.log` - logi głównego modułu
- `mini_dashboard.log` - logi mini dashboardu
- `simple_dashboard.log` - logi pełnego dashboardu
- `notification_service.log` - logi serwisu powiadomień
- `parallel_executor.log` - logi równoległego wykonawcy
- `flow_scheduler.log` - logi planera
- `email_pipeline.log` - logi procesora email

## FAQ

Zobacz [FAQ](./faq.md) dla najczęściej zadawanych pytań.

<!-- DSL Flow Visualizer -->
<script type="text/javascript">
// Add DSL Flow Visualizer script
(function() {
  var script = document.createElement('script');
  script.src = '/static/js/dsl-flow-visualizer.js';
  script.async = true;
  script.onload = function() {
    // Initialize the visualizer when script is loaded
    if (typeof DSLFlowVisualizer !== 'undefined') {
      new DSLFlowVisualizer();
    }
  };
  document.head.appendChild(script);
  
  // Add CSS styles
  var style = document.createElement('style');
  style.textContent = `
    .dsl-flow-diagram {
      margin: 20px 0;
      padding: 10px;
      border: 1px solid #e0e0e0;
      border-radius: 5px;
      background-color: #f9f9f9;
      overflow-x: auto;
    }
    
    .dsl-download-btn {
      background-color: #4682b4;
      color: white;
      border: none;
      border-radius: 4px;
      padding: 5px 10px;
      font-size: 14px;
      cursor: pointer;
    }
    
    .dsl-download-btn:hover {
      background-color: #36648b;
    }
  `;
  document.head.appendChild(style);
  
  // Add language class to DSL code blocks if not already present
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('pre code').forEach(function(codeBlock) {
      var content = codeBlock.textContent.trim();
      if (content.startsWith('flow ') && !codeBlock.classList.contains('language-dsl')) {
        codeBlock.classList.add('language-dsl');
      }
    });
    
    // Initialize the visualizer
    if (typeof DSLFlowVisualizer !== 'undefined') {
      new DSLFlowVisualizer();
    }
  });
})();
</script>
