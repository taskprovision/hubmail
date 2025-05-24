# Najczęściej Zadawane Pytania (FAQ)

## Spis treści

- [Ogólne pytania](#ogólne-pytania)
- [Instalacja i konfiguracja](#instalacja-i-konfiguracja)
- [Definiowanie przepływów](#definiowanie-przepływów)
- [Uruchamianie przepływów](#uruchamianie-przepływów)
- [Wizualizacja](#wizualizacja)
- [Dashboard](#dashboard)
- [Powiadomienia](#powiadomienia)
- [Równoległe wykonanie](#równoległe-wykonanie)
- [Planowanie przepływów](#planowanie-przepływów)
- [Przetwarzanie email](#przetwarzanie-email)
- [Rozwiązywanie problemów](#rozwiązywanie-problemów)

## Ogólne pytania

### Czym jest taskinity?

taskinity to lekki framework do definiowania i uruchamiania przepływów zadań za pomocą prostego języka DSL i dekoratorów Python. Jest znacznie prostszy niż Prefect, Airflow czy Luigi i działa natychmiast bez skomplikowanej konfiguracji.

### Jakie są główne zalety taskinity?

- **Prostota** - minimalny zestaw funkcji, łatwy do zrozumienia i rozszerzenia
- **Dekoratory** - intuicyjny sposób definiowania zadań i przepływów
- **DSL** - prosty język do definiowania połączeń między zadaniami
- **Brak zależności zewnętrznych** - działa natychmiast, bez skomplikowanej konfiguracji
- **Lekki monitoring** - automatyczne logowanie i śledzenie wykonania
- **Wizualizacja** - proste narzędzia do wizualizacji przepływów
- **Walidacja danych** - możliwość walidacji danych wejściowych i wyjściowych

### Czy taskinity jest odpowiedni dla dużych projektów?

taskinity jest idealny dla małych i średnich projektów. Dla dużych projektów z setkami zadań i skomplikowaną logiką, warto rozważyć bardziej zaawansowane narzędzia jak Airflow czy Prefect. Jednak nawet w dużych projektach taskinity może być używany do prototypowania i szybkiego testowania przepływów.

### Czy taskinity jest aktywnie rozwijany?

Tak, taskinity jest aktywnie rozwijany. Regularnie dodajemy nowe funkcje i ulepszenia, takie jak równoległe wykonanie, planowanie przepływów i przetwarzanie email.

## Instalacja i konfiguracja

### Jak zainstalować taskinity?

taskinity nie wymaga skomplikowanej instalacji. Wystarczy sklonować repozytorium i zainstalować zależności:

```bash
# Klonowanie repozytorium
git clone https://github.com/taskinity/hubmail.git
cd hubmail/dsl

# Instalacja zależności
pip install -r requirements.txt
```

### Jakie są wymagania systemowe?

- Python 3.7+
- Zależności wymienione w `requirements.txt`

### Czy taskinity działa na Windows/Linux/macOS?

Tak, taskinity działa na wszystkich głównych systemach operacyjnych: Windows, Linux i macOS.

### Czy mogę używać taskinity w kontenerach Docker?

Tak, taskinity może być łatwo uruchamiany w kontenerach Docker. W repozytorium znajduje się przykładowy plik `Dockerfile.dashboard` i `docker-compose-email.yml`.

## Definiowanie przepływów

### Jak zdefiniować zadanie w taskinity?

Zadania definiuje się za pomocą dekoratora `@task`:

```python
from flow_dsl import task

@task(name="Pobieranie danych", description="Pobiera dane z API")
def fetch_data(url: str):
    # Implementacja
    return data
```

### Jak zdefiniować przepływ w taskinity?

Przepływy definiuje się za pomocą prostego języka DSL:

```python
flow_dsl = """
flow DataProcessing:
    description: "Przetwarzanie danych"
    fetch_data -> process_data
    process_data -> save_results
"""
```

### Czy mogę łączyć jedno zadanie z wieloma zadaniami?

Tak, możesz łączyć jedno zadanie z wieloma zadaniami:

```python
flow_dsl = """
flow DataProcessing:
    description: "Przetwarzanie danych"
    fetch_data -> process_data
    fetch_data -> log_data
    process_data -> save_results
"""
```

### Czy mogę definiować warunki w przepływach?

Obecnie taskinity nie obsługuje bezpośrednio warunków w definicji DSL. Możesz jednak implementować logikę warunkową wewnątrz zadań.

## Uruchamianie przepływów

### Jak uruchomić przepływ?

Przepływy uruchamia się za pomocą funkcji `run_flow_from_dsl`:

```python
from flow_dsl import run_flow_from_dsl

results = run_flow_from_dsl(flow_dsl, {"url": "https://example.com/data"})
```

### Jak przekazać dane wejściowe do przepływu?

Dane wejściowe przekazuje się jako drugi argument funkcji `run_flow_from_dsl`:

```python
results = run_flow_from_dsl(flow_dsl, {
    "url": "https://example.com/data",
    "api_key": "your_api_key"
})
```

### Jak uzyskać wyniki przepływu?

Wyniki przepływu są zwracane przez funkcję `run_flow_from_dsl`:

```python
results = run_flow_from_dsl(flow_dsl, input_data)
print(results)
```

### Czy mogę uruchomić przepływ z pliku DSL?

Tak, możesz wczytać definicję DSL z pliku:

```python
from flow_dsl import load_dsl, run_flow_from_dsl

dsl_content = load_dsl("dsl_definitions/my_flow.dsl")
results = run_flow_from_dsl(dsl_content, input_data)
```

## Wizualizacja

### Jak wizualizować przepływ?

taskinity zawiera narzędzia do wizualizacji przepływów:

```python
from flow_visualizer import visualize_dsl

visualize_dsl(flow_dsl, output_file="flow_diagram.png")
```

### Jakie formaty wizualizacji są obsługiwane?

taskinity obsługuje wizualizację w formatach PNG, SVG i Mermaid.

### Czy mogę wizualizować historię wykonania przepływu?

Tak, możesz wizualizować historię wykonania przepływu:

```python
from flow_visualizer import visualize_flow

visualize_flow(flow_id, output_file="execution_diagram.png")
```

### Jak wizualizować przepływy w dashboardzie?

Dashboard automatycznie wizualizuje przepływy. Wystarczy uruchomić dashboard i przejść do zakładki "Wizualizacja".

## Dashboard

### Jak uruchomić dashboard?

taskinity zawiera dwa dashboardy:

1. **Mini Dashboard**:
```bash
python mini_dashboard.py
```

2. **Pełny Dashboard**:
```bash
python simple_dashboard.py
```

### Jakie funkcje oferuje dashboard?

- Przeglądanie definicji DSL
- Uruchamianie przepływów
- Przeglądanie historii wykonania
- Wizualizacja przepływów
- Przeglądanie logów
- Konfiguracja powiadomień
- Zarządzanie harmonogramami

### Na jakim porcie działa dashboard?

Mini Dashboard działa domyślnie na porcie 8765, a Pełny Dashboard na porcie 8000.

### Czy mogę zmienić port dashboardu?

Tak, możesz zmienić port dashboardu, edytując odpowiedni plik:

```python
# mini_dashboard.py
app.run(host="0.0.0.0", port=8765)  # Zmień port na wybrany
```

## Powiadomienia

### Jak skonfigurować powiadomienia email?

Powiadomienia email konfiguruje się w pliku `config/notification_config.json`:

```json
{
    "enabled": true,
    "email": {
        "enabled": true,
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "username": "user@example.com",
        "password": "password123",
        "from_email": "taskinity@example.com",
        "recipients": ["admin@example.com"]
    }
}
```

### Jak skonfigurować powiadomienia Slack?

Powiadomienia Slack konfiguruje się w pliku `config/notification_config.json`:

```json
{
    "enabled": true,
    "slack": {
        "enabled": true,
        "webhook_url": "https://hooks.slack.com/services/XXX/YYY/ZZZ",
        "channel": "#flow-notifications",
        "username": "taskinity Bot"
    }
}
```

### Kiedy są wysyłane powiadomienia?

Powiadomienia są wysyłane w zależności od konfiguracji w sekcji `notification_rules`:

```json
{
    "notification_rules": {
        "on_start": true,
        "on_complete": true,
        "on_error": true,
        "include_details": true
    }
}
```

### Jak wysłać powiadomienie ręcznie?

Możesz wysłać powiadomienie ręcznie za pomocą funkcji `send_email_notification` i `send_slack_notification`:

```python
from notification_service import send_email_notification, send_slack_notification

send_email_notification("Temat", "Treść wiadomości")
send_slack_notification("Tytuł", "Treść wiadomości")
```

## Równoległe wykonanie

### Jak uruchomić przepływ z równoległym wykonaniem?

Przepływy z równoległym wykonaniem uruchamia się za pomocą funkcji `run_parallel_flow_from_dsl`:

```python
from parallel_executor import run_parallel_flow_from_dsl

results = run_parallel_flow_from_dsl(flow_dsl, input_data)
```

### Jakie są ograniczenia równoległego wykonania?

Równoległe wykonanie ma następujące ograniczenia:
- Zadania muszą być niezależne od siebie
- Zadania nie mogą modyfikować tych samych danych
- Zadania muszą być bezpieczne wątkowo

### Jak kontrolować liczbę równoległych zadań?

Możesz kontrolować liczbę równoległych zadań za pomocą parametru `max_workers`:

```python
results = run_parallel_flow_from_dsl(flow_dsl, input_data, max_workers=4)
```

### Czy równoległe wykonanie jest szybsze?

Równoległe wykonanie jest szybsze dla przepływów z niezależnymi zadaniami, które mogą być wykonywane jednocześnie. Dla przepływów sekwencyjnych nie ma różnicy w wydajności.

## Planowanie przepływów

### Jak zaplanować wykonanie przepływu?

Przepływy planuje się za pomocą modułu `flow_scheduler`:

```python
from flow_scheduler import Scheduler

scheduler = Scheduler()
scheduler.add_schedule("dsl_definitions/my_flow.dsl", interval=60)
scheduler.start()
```

### Jakie typy harmonogramów są obsługiwane?

taskinity obsługuje następujące typy harmonogramów:
- Interwałowy (co X minut)
- Dzienny (o określonej godzinie)
- Tygodniowy (w określony dzień tygodnia)
- Miesięczny (w określony dzień miesiąca)

### Jak zarządzać harmonogramami z linii poleceń?

Możesz zarządzać harmonogramami za pomocą linii poleceń:

```bash
# Uruchomienie planera
python flow_scheduler.py start

# Utworzenie harmonogramu (co 60 minut)
python flow_scheduler.py create dsl_definitions/my_flow.dsl 60

# Lista harmonogramów
python flow_scheduler.py list

# Ręczne uruchomienie harmonogramu
python flow_scheduler.py run [schedule_id]

# Usunięcie harmonogramu
python flow_scheduler.py delete [schedule_id]
```

### Czy mogę przekazać dane wejściowe do zaplanowanego przepływu?

Tak, możesz przekazać dane wejściowe do zaplanowanego przepływu:

```python
scheduler.add_schedule(
    "dsl_definitions/my_flow.dsl",
    interval=60,
    input_data={"url": "https://example.com/data"}
)
```

## Przetwarzanie email

### Jak skonfigurować przetwarzanie email?

Przetwarzanie email konfiguruje się w pliku `config/email_config.json`:

```json
{
    "imap": {
        "server": "imap.example.com",
        "port": 993,
        "username": "user@example.com",
        "password": "password123",
        "folder": "INBOX",
        "ssl": true
    },
    "smtp": {
        "server": "smtp.example.com",
        "port": 587,
        "username": "user@example.com",
        "password": "password123",
        "from_email": "user@example.com",
        "use_tls": true
    }
}
```

### Jak uruchomić przetwarzanie email?

Przetwarzanie email uruchamia się za pomocą modułu `email_pipeline`:

```python
from email_pipeline import EmailProcessor

processor = EmailProcessor()
processor.process_emails()
```

### Jak skonfigurować automatyczne odpowiedzi?

Automatyczne odpowiedzi konfiguruje się w sekcji `auto_reply` pliku `config/email_config.json`:

```json
{
    "auto_reply": {
        "enabled": true,
        "criteria": {
            "subject_contains": ["pytanie", "zapytanie", "pomoc", "wsparcie"],
            "from_domains": ["example.com", "gmail.com"],
            "priority_keywords": ["pilne", "ważne", "urgent", "asap"]
        },
        "templates": {
            "default": "Dziękujemy za wiadomość. Odpowiemy najszybciej jak to możliwe.",
            "priority": "Dziękujemy za pilną wiadomość. Zajmiemy się nią priorytetowo.",
            "support": "Dziękujemy za zgłoszenie. Nasz zespół wsparcia skontaktuje się z Tobą wkrótce."
        }
    }
}
```

### Jak uruchomić przepływ na podstawie emaila?

Uruchamianie przepływów na podstawie emaili konfiguruje się w sekcji `flows` pliku `config/email_config.json`:

```json
{
    "flows": {
        "trigger_flow_on_email": true,
        "flow_mapping": {
            "support": "support_flow.dsl",
            "order": "order_processing.dsl",
            "complaint": "complaint_handling.dsl"
        }
    }
}
```

## Rozwiązywanie problemów

### Jak rozwiązać problem z parsowaniem DSL?

Sprawdź składnię DSL, zwracając uwagę na:
- Wcięcia i spacje
- Poprawność nazw zadań
- Poprawność połączeń między zadaniami

### Jak rozwiązać problem z uruchamianiem przepływów?

Sprawdź:
- Czy wszystkie zadania są poprawnie zdefiniowane
- Czy dane wejściowe są poprawne
- Czy nie ma błędów w implementacji zadań

### Jak rozwiązać problem z powiadomieniami?

Sprawdź:
- Konfigurację SMTP/Slack
- Czy powiadomienia są włączone
- Logi serwisu powiadomień

### Gdzie znaleźć logi?

Logi znajdują się w katalogu `logs/`:
- `flow_dsl.log` - logi głównego modułu
- `mini_dashboard.log` - logi mini dashboardu
- `simple_dashboard.log` - logi pełnego dashboardu
- `notification_service.log` - logi serwisu powiadomień
- `parallel_executor.log` - logi równoległego wykonawcy
- `flow_scheduler.log` - logi planera
- `email_pipeline.log` - logi procesora email

<!-- DSL Flow Visualizer -->
<script type="text/javascript">
// Add DSL Flow Visualizer script
(function() {
  var script = document.createElement('script');
  script.src = '/hubmail/dsl/static/js/dsl-flow-visualizer.js';
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


<!-- Markdown Enhancements -->

<!-- Taskinity Markdown Enhancements -->
<!-- Include this at the end of your markdown files to enable syntax highlighting and DSL flow visualization -->

<!-- Prism.js for syntax highlighting -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>

<!-- Load common language components -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-javascript.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-yaml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-markdown.min.js"></script>

<!-- Taskinity custom scripts -->
<script src="../../static/js/dsl-flow-visualizer.js"></script>
<script src="../../static/js/markdown-syntax-highlighter.js"></script>

<script>
  // Initialize both scripts when the page loads
  document.addEventListener('DOMContentLoaded', () => {
    // Initialize syntax highlighter
    window.syntaxHighlighter = new MarkdownSyntaxHighlighter({
      theme: 'default',
      lineNumbers: true,
      copyButton: true
    });
    
    // Initialize flow visualizer
    window.flowVisualizer = new DSLFlowVisualizer({
      codeBlockSelector: 'pre code.language-dsl, pre code.language-flow'
    });
  });
</script>

<!-- Custom styles for better markdown rendering -->
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
  }
  
  pre {
    border-radius: 5px;
    background-color: #f5f5f5;
    padding: 15px;
    overflow: auto;
  }
  
  code {
    font-family: 'Fira Code', 'Courier New', Courier, monospace;
  }
  
  h1, h2, h3, h4, h5, h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    color: #2c3e50;
  }
  
  a {
    color: #3498db;
    text-decoration: none;
  }
  
  a:hover {
    text-decoration: underline;
  }
  
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
  }
  
  table, th, td {
    border: 1px solid #ddd;
  }
  
  th, td {
    padding: 12px;
    text-align: left;
  }
  
  th {
    background-color: #f2f2f2;
  }
  
  blockquote {
    border-left: 4px solid #3498db;
    padding-left: 15px;
    color: #666;
    margin: 20px 0;
  }
  
  img {
    max-width: 100%;
    height: auto;
  }
  
  .dsl-flow-diagram {
    margin: 20px 0;
    padding: 15px;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    background-color: #f9f9f9;
  }
</style>
