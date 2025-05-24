# Samouczek taskinity

## Spis treści

- [Wprowadzenie](#wprowadzenie)
- [Krok 1: Instalacja](#krok-1-instalacja)
- [Krok 2: Tworzenie pierwszego zadania](#krok-2-tworzenie-pierwszego-zadania)
- [Krok 3: Definiowanie przepływu](#krok-3-definiowanie-przepływu)
- [Krok 4: Uruchamianie przepływu](#krok-4-uruchamianie-przepływu)
- [Krok 5: Wizualizacja przepływu](#krok-5-wizualizacja-przepływu)
- [Krok 6: Monitorowanie i logi](#krok-6-monitorowanie-i-logi)
- [Krok 7: Korzystanie z dashboardu](#krok-7-korzystanie-z-dashboardu)
- [Krok 8: Konfiguracja powiadomień](#krok-8-konfiguracja-powiadomień)
- [Krok 9: Równoległe wykonanie](#krok-9-równoległe-wykonanie)
- [Krok 10: Planowanie przepływów](#krok-10-planowanie-przepływów)
- [Następne kroki](#następne-kroki)

## Wprowadzenie

taskinity to lekki framework do definiowania i uruchamiania przepływów zadań. W tym samouczku przeprowadzimy Cię krok po kroku przez proces tworzenia, uruchamiania i zarządzania przepływami zadań za pomocą taskinity.

## Krok 1: Instalacja

taskinity nie wymaga skomplikowanej instalacji. Wystarczy sklonować repozytorium i zainstalować zależności:

```bash
# Klonowanie repozytorium
git clone https://github.com/taskinity/hubmail.git
cd hubmail/dsl

# Instalacja zależności
pip install -r requirements.txt
```

## Krok 2: Tworzenie pierwszego zadania

Zadania w taskinity definiuje się za pomocą dekoratora `@task`. Utwórz plik `my_flow.py` i dodaj do niego pierwsze zadanie:

```python
from flow_dsl import task

@task(name="Pobieranie danych", description="Pobiera dane z API")
def fetch_data(url: str):
    print(f"Pobieranie danych z {url}")
    # W rzeczywistej aplikacji tutaj byłby kod do pobierania danych
    return {"data": [1, 2, 3, 4, 5]}

@task(name="Przetwarzanie danych", description="Przetwarza pobrane dane")
def process_data(data):
    print(f"Przetwarzanie danych: {data}")
    # W rzeczywistej aplikacji tutaj byłby kod do przetwarzania danych
    processed_data = [x * 2 for x in data["data"]]
    return {"processed_data": processed_data}

@task(name="Zapisywanie wyników", description="Zapisuje przetworzone dane")
def save_results(processed_data):
    print(f"Zapisywanie wyników: {processed_data}")
    # W rzeczywistej aplikacji tutaj byłby kod do zapisywania danych
    return {"status": "success", "count": len(processed_data["processed_data"])}
```

## Krok 3: Definiowanie przepływu

Teraz zdefiniujmy przepływ, który połączy nasze zadania. Dodaj do pliku `my_flow.py`:

```python
# Definicja przepływu DSL
flow_dsl = """
flow DataProcessing:
    description: "Przetwarzanie danych"
    fetch_data -> process_data
    process_data -> save_results
"""
```

Przepływ `DataProcessing` składa się z trzech zadań:
1. `fetch_data` - pobiera dane
2. `process_data` - przetwarza dane
3. `save_results` - zapisuje wyniki

Zadania są połączone w sekwencję: `fetch_data -> process_data -> save_results`.

## Krok 4: Uruchamianie przepływu

Teraz uruchomimy nasz przepływ. Dodaj do pliku `my_flow.py`:

```python
from flow_dsl import run_flow_from_dsl

if __name__ == "__main__":
    # Uruchomienie przepływu
    results = run_flow_from_dsl(flow_dsl, {"url": "https://example.com/data"})
    
    # Wyświetlenie wyników
    print("\nWyniki przepływu:")
    print(results)
```

Uruchom plik:

```bash
python my_flow.py
```

Powinieneś zobaczyć wyniki wykonania przepływu:

```
Pobieranie danych z https://example.com/data
Przetwarzanie danych: {'data': [1, 2, 3, 4, 5]}
Zapisywanie wyników: {'processed_data': [2, 4, 6, 8, 10]}

Wyniki przepływu:
{'fetch_data': {'data': [1, 2, 3, 4, 5]}, 'process_data': {'processed_data': [2, 4, 6, 8, 10]}, 'save_results': {'status': 'success', 'count': 5}}
```

## Krok 5: Wizualizacja przepływu

taskinity umożliwia wizualizację przepływów. Dodaj do pliku `my_flow.py`:

```python
from flow_visualizer import visualize_dsl

if __name__ == "__main__":
    # Uruchomienie przepływu
    results = run_flow_from_dsl(flow_dsl, {"url": "https://example.com/data"})
    
    # Wyświetlenie wyników
    print("\nWyniki przepływu:")
    print(results)
    
    # Wizualizacja przepływu
    visualize_dsl(flow_dsl, output_file="my_flow.png")
    print("\nWizualizacja przepływu zapisana do pliku my_flow.png")
```

Uruchom plik:

```bash
python my_flow.py
```

Powinieneś zobaczyć komunikat o zapisaniu wizualizacji do pliku `my_flow.png`. Otwórz ten plik, aby zobaczyć diagram przepływu.

## Krok 6: Monitorowanie i logi

taskinity automatycznie zapisuje logi wykonania przepływów. Sprawdźmy, jak możemy je przeglądać:

```python
import json
from pathlib import Path

def view_flow_logs(flow_id):
    flow_file = Path("flows") / f"{flow_id}.json"
    if not flow_file.exists():
        print(f"Nie znaleziono przepływu o ID: {flow_id}")
        return
    
    with open(flow_file, "r") as f:
        flow_data = json.load(f)
    
    print(f"Przepływ: {flow_data['name']}")
    print(f"Status: {flow_data['status']}")
    print(f"Czas rozpoczęcia: {flow_data['start_time']}")
    print(f"Czas zakończenia: {flow_data['end_time']}")
    print("\nZadania:")
    
    for task_id, task_data in flow_data["tasks"].items():
        print(f"  - {task_id}: {task_data['status']}")
        if task_data.get("error"):
            print(f"    Błąd: {task_data['error']}")

if __name__ == "__main__":
    # Uruchomienie przepływu
    results = run_flow_from_dsl(flow_dsl, {"url": "https://example.com/data"})
    
    # Wyświetlenie ID przepływu
    flow_id = results.get("_flow_id")
    print(f"\nID przepływu: {flow_id}")
    
    # Przeglądanie logów przepływu
    print("\nLogi przepływu:")
    view_flow_logs(flow_id)
```

## Krok 7: Korzystanie z dashboardu

taskinity zawiera dashboard do zarządzania przepływami. Uruchom mini dashboard:

```bash
python mini_dashboard.py
```

Dashboard będzie dostępny pod adresem http://localhost:8765. Możesz:
- Przeglądać definicje DSL
- Uruchamiać przepływy
- Przeglądać historię wykonania
- Wizualizować przepływy
- Przeglądać logi

## Krok 8: Konfiguracja powiadomień

taskinity umożliwia wysyłanie powiadomień o statusie przepływów. Skonfigurujmy powiadomienia email:

```python
from notification_service import load_config, save_config, send_email_notification

# Załadowanie konfiguracji
config = load_config()

# Konfiguracja powiadomień email
config["enabled"] = True
config["email"]["enabled"] = True
config["email"]["smtp_server"] = "smtp.example.com"
config["email"]["smtp_port"] = 587
config["email"]["username"] = "user@example.com"
config["email"]["password"] = "password123"
config["email"]["from_email"] = "taskinity@example.com"
config["email"]["recipients"] = ["admin@example.com"]

# Zapisanie konfiguracji
save_config(config)

# Wysłanie testowego powiadomienia
send_email_notification("Test powiadomień taskinity", "To jest testowe powiadomienie z taskinity.")
```

## Krok 9: Równoległe wykonanie

taskinity umożliwia równoległe wykonanie niezależnych zadań. Zmodyfikujmy nasz przepływ, aby wykorzystać równoległe wykonanie:

```python
from flow_dsl import task
from parallel_executor import run_parallel_flow_from_dsl

@task(name="Pobieranie danych A", description="Pobiera dane z API A")
def fetch_data_a(url: str):
    print(f"Pobieranie danych A z {url}/a")
    return {"data_a": [1, 2, 3]}

@task(name="Pobieranie danych B", description="Pobiera dane z API B")
def fetch_data_b(url: str):
    print(f"Pobieranie danych B z {url}/b")
    return {"data_b": [4, 5, 6]}

@task(name="Łączenie danych", description="Łączy dane z różnych źródeł")
def merge_data(data_a, data_b):
    print(f"Łączenie danych: {data_a} i {data_b}")
    merged_data = data_a["data_a"] + data_b["data_b"]
    return {"merged_data": merged_data}

# Definicja przepływu DSL z równoległym wykonaniem
parallel_flow_dsl = """
flow ParallelDataProcessing:
    description: "Równoległe przetwarzanie danych"
    fetch_data_a -> merge_data
    fetch_data_b -> merge_data
"""

if __name__ == "__main__":
    # Uruchomienie przepływu z równoległym wykonaniem
    results = run_parallel_flow_from_dsl(parallel_flow_dsl, {"url": "https://example.com"})
    
    # Wyświetlenie wyników
    print("\nWyniki przepływu równoległego:")
    print(results)
```

## Krok 10: Planowanie przepływów

taskinity pozwala na planowanie automatycznego wykonania przepływów. Utwórzmy harmonogram dla naszego przepływu:

```python
from flow_scheduler import Scheduler

# Zapisanie definicji DSL do pliku
with open("dsl_definitions/data_processing.dsl", "w") as f:
    f.write(flow_dsl)

# Utworzenie planera
scheduler = Scheduler()

# Dodanie harmonogramu (co 60 minut)
scheduler.add_schedule("dsl_definitions/data_processing.dsl", interval=60)

# Uruchomienie planera
scheduler.start()
```

Możesz również zarządzać harmonogramami za pomocą linii poleceń:

```bash
# Uruchomienie planera
python flow_scheduler.py start

# Utworzenie harmonogramu (co 60 minut)
python flow_scheduler.py create dsl_definitions/data_processing.dsl 60

# Lista harmonogramów
python flow_scheduler.py list

# Ręczne uruchomienie harmonogramu
python flow_scheduler.py run [schedule_id]

# Usunięcie harmonogramu
python flow_scheduler.py delete [schedule_id]
```

## Następne kroki

Gratulacje! Przeszedłeś przez podstawowe funkcje taskinity. Oto kilka pomysłów na dalsze kroki:

1. **Zaawansowane przepływy** - twórz bardziej złożone przepływy z warunkami i pętlami
2. **Integracja z innymi systemami** - integruj taskinity z bazami danych, API i innymi systemami
3. **Rozszerzanie funkcjonalności** - dodawaj własne funkcje i moduły do taskinity
4. **Automatyzacja procesów** - automatyzuj powtarzalne procesy za pomocą taskinity

Więcej informacji znajdziesz w [dokumentacji technicznej](./dokumentacja.md) i [przykładach](./przyklady.md).

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
