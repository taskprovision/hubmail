# Przykłady taskinity

## Spis treści

- [Podstawowe przepływy](#podstawowe-przepływy)
- [Przetwarzanie danych](#przetwarzanie-danych)
- [Integracja z API](#integracja-z-api)
- [Przetwarzanie emaili](#przetwarzanie-emaili)
- [Analiza danych](#analiza-danych)
- [Równoległe wykonanie](#równoległe-wykonanie)
- [Planowanie przepływów](#planowanie-przepływów)

## Podstawowe przepływy

### Prosty przepływ sekwencyjny

```python
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
print(results)
```

### Przepływ z rozgałęzieniem

```python
from flow_dsl import task, run_flow_from_dsl

@task(name="Pobieranie danych")
def fetch_data():
    return {"data": [1, 2, 3, 4, 5]}

@task(name="Filtrowanie danych")
def filter_data(input_data):
    data = input_data["data"]
    filtered = [x for x in data if x % 2 == 0]
    return {"filtered_data": filtered}

@task(name="Transformacja danych")
def transform_data(input_data):
    data = input_data["data"]
    transformed = [x * 2 for x in data]
    return {"transformed_data": transformed}

@task(name="Łączenie wyników")
def merge_results(filtered_data, transformed_data):
    return {
        "filtered": filtered_data["filtered_data"],
        "transformed": transformed_data["transformed_data"]
    }

# Definicja przepływu DSL
flow_dsl = """
flow BranchingFlow:
    description: "Przepływ z rozgałęzieniem"
    fetch_data -> filter_data
    fetch_data -> transform_data
    filter_data -> merge_results
    transform_data -> merge_results
"""

# Uruchomienie przepływu
results = run_flow_from_dsl(flow_dsl, {})
print(results)
```

## Przetwarzanie danych

### Przetwarzanie CSV

```python
from flow_dsl import task, run_flow_from_dsl
import pandas as pd

@task(name="Wczytanie CSV")
def load_csv(file_path):
    df = pd.read_csv(file_path)
    return {"dataframe": df}

@task(name="Czyszczenie danych")
def clean_data(input_data):
    df = input_data["dataframe"]
    # Usunięcie duplikatów
    df = df.drop_duplicates()
    # Usunięcie wierszy z brakującymi wartościami
    df = df.dropna()
    return {"dataframe": df}

@task(name="Transformacja danych")
def transform_data(input_data):
    df = input_data["dataframe"]
    # Przykładowa transformacja - konwersja kolumny na wielkie litery
    if "name" in df.columns:
        df["name"] = df["name"].str.upper()
    return {"dataframe": df}

@task(name="Zapisanie wyników")
def save_results(input_data, output_path):
    df = input_data["dataframe"]
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

# Uruchomienie przepływu
results = run_flow_from_dsl(flow_dsl, {
    "file_path": "data/input.csv",
    "output_path": "data/output.csv"
})
print(results)
```

## Integracja z API

### Pobieranie danych z API i zapisywanie do bazy danych

```python
from flow_dsl import task, run_flow_from_dsl
import requests
import sqlite3

@task(name="Pobieranie danych z API")
def fetch_from_api(api_url):
    response = requests.get(api_url)
    response.raise_for_status()
    return {"data": response.json()}

@task(name="Przetwarzanie danych")
def process_api_data(input_data):
    data = input_data["data"]
    # Przykładowe przetwarzanie - ekstrakcja potrzebnych pól
    processed = [{"id": item["id"], "name": item["name"], "value": item["value"]} 
                for item in data if "value" in item]
    return {"processed_data": processed}

@task(name="Zapisanie do bazy danych")
def save_to_database(input_data, db_path):
    processed_data = input_data["processed_data"]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Utworzenie tabeli, jeśli nie istnieje
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT,
        value REAL
    )
    ''')
    
    # Wstawienie danych
    for item in processed_data:
        cursor.execute(
            "INSERT OR REPLACE INTO items (id, name, value) VALUES (?, ?, ?)",
            (item["id"], item["name"], item["value"])
        )
    
    conn.commit()
    conn.close()
    
    return {"items_saved": len(processed_data)}

# Definicja przepływu DSL
flow_dsl = """
flow APIToDatabaseFlow:
    description: "Pobieranie danych z API i zapisywanie do bazy danych"
    fetch_from_api -> process_api_data
    process_api_data -> save_to_database
"""

# Uruchomienie przepływu
results = run_flow_from_dsl(flow_dsl, {
    "api_url": "https://api.example.com/data",
    "db_path": "data/database.sqlite"
})
print(results)
```

## Przetwarzanie emaili

### Automatyczne odpowiedzi na emaile

```python
from flow_dsl import task, run_flow_from_dsl
from email_pipeline import EmailProcessor

@task(name="Pobieranie emaili")
def fetch_emails(config):
    processor = EmailProcessor(config)
    emails = processor.fetch_emails()
    return {"emails": emails}

@task(name="Klasyfikacja emaili")
def classify_emails(input_data):
    emails = input_data["emails"]
    
    support_emails = []
    order_emails = []
    other_emails = []
    
    for email in emails:
        subject = email["subject"].lower()
        if "support" in subject or "help" in subject:
            support_emails.append(email)
        elif "order" in subject or "purchase" in subject:
            order_emails.append(email)
        else:
            other_emails.append(email)
    
    return {
        "support_emails": support_emails,
        "order_emails": order_emails,
        "other_emails": other_emails
    }

@task(name="Odpowiedź na emaile wsparcia")
def reply_to_support(input_data, config):
    emails = input_data["support_emails"]
    processor = EmailProcessor(config)
    
    for email in emails:
        processor.send_auto_reply(email, "support")
    
    return {"replied_count": len(emails)}

@task(name="Odpowiedź na emaile zamówień")
def reply_to_orders(input_data, config):
    emails = input_data["order_emails"]
    processor = EmailProcessor(config)
    
    for email in emails:
        processor.send_auto_reply(email, "order")
    
    return {"replied_count": len(emails)}

@task(name="Odpowiedź na pozostałe emaile")
def reply_to_others(input_data, config):
    emails = input_data["other_emails"]
    processor = EmailProcessor(config)
    
    for email in emails:
        processor.send_auto_reply(email, "default")
    
    return {"replied_count": len(emails)}

# Definicja przepływu DSL
flow_dsl = """
flow EmailProcessing:
    description: "Przetwarzanie i automatyczne odpowiedzi na emaile"
    fetch_emails -> classify_emails
    classify_emails -> reply_to_support
    classify_emails -> reply_to_orders
    classify_emails -> reply_to_others
"""

# Uruchomienie przepływu
results = run_flow_from_dsl(flow_dsl, {
    "config": {
        "imap": {
            "server": "imap.example.com",
            "port": 993,
            "username": "user@example.com",
            "password": "password123",
            "folder": "INBOX",
            "ssl": True
        },
        "smtp": {
            "server": "smtp.example.com",
            "port": 587,
            "username": "user@example.com",
            "password": "password123",
            "from_email": "user@example.com",
            "use_tls": True
        },
        "auto_reply": {
            "enabled": True,
            "templates": {
                "support": "Dziękujemy za zgłoszenie. Nasz zespół wsparcia skontaktuje się z Tobą wkrótce.",
                "order": "Dziękujemy za zamówienie. Potwierdzamy jego otrzymanie i wkrótce rozpoczniemy realizację.",
                "default": "Dziękujemy za wiadomość. Odpowiemy najszybciej jak to możliwe."
            }
        }
    }
})
print(results)
```

## Analiza danych

### Analiza sentymentu tekstu

```python
from flow_dsl import task, run_flow_from_dsl
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

@task(name="Inicjalizacja analizatora")
def init_analyzer():
    # Pobranie potrzebnych danych NLTK
    nltk.download('vader_lexicon')
    analyzer = SentimentIntensityAnalyzer()
    return {"analyzer": analyzer}

@task(name="Wczytanie tekstów")
def load_texts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        texts = [line.strip() for line in f if line.strip()]
    return {"texts": texts}

@task(name="Analiza sentymentu")
def analyze_sentiment(analyzer_data, texts_data):
    analyzer = analyzer_data["analyzer"]
    texts = texts_data["texts"]
    
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
    "file_path": "data/texts.txt"
})
print(results)
```

## Równoległe wykonanie

### Równoległe przetwarzanie plików

```python
from flow_dsl import task
from parallel_executor import run_parallel_flow_from_dsl
import os

@task(name="Skanowanie katalogu")
def scan_directory(directory_path):
    files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) 
             if os.path.isfile(os.path.join(directory_path, f))]
    return {"files": files}

@task(name="Przetwarzanie pliku")
def process_file(file_path):
    # Przykładowe przetwarzanie - zliczanie linii w pliku
    with open(file_path, 'r', encoding='utf-8') as f:
        line_count = sum(1 for _ in f)
    
    return {
        "file_path": file_path,
        "file_name": os.path.basename(file_path),
        "line_count": line_count
    }

@task(name="Agregacja wyników")
def aggregate_results(processed_files):
    total_files = len(processed_files)
    total_lines = sum(file_data["line_count"] for file_data in processed_files)
    
    return {
        "total_files": total_files,
        "total_lines": total_lines,
        "average_lines": total_lines / total_files if total_files > 0 else 0,
        "files_details": processed_files
    }

# Definicja przepływu DSL z równoległym wykonaniem
flow_dsl = """
flow ParallelFileProcessing:
    description: "Równoległe przetwarzanie plików"
    scan_directory -> process_file
    process_file -> aggregate_results
"""

# Uruchomienie przepływu z równoległym wykonaniem
results = run_parallel_flow_from_dsl(flow_dsl, {
    "directory_path": "data/files"
})
print(results)
```

## Planowanie przepływów

### Planowanie codziennego raportu

```python
from flow_dsl import task, run_flow_from_dsl
from flow_scheduler import Scheduler
import datetime
import pandas as pd

@task(name="Pobieranie danych sprzedaży")
def fetch_sales_data(date):
    # Symulacja pobierania danych sprzedaży dla danego dnia
    # W rzeczywistej aplikacji tutaj byłby kod do pobierania danych z bazy lub API
    sales_data = [
        {"product": "Produkt A", "quantity": 10, "price": 100},
        {"product": "Produkt B", "quantity": 5, "price": 200},
        {"product": "Produkt C", "quantity": 8, "price": 150}
    ]
    return {"sales_data": sales_data, "date": date}

@task(name="Generowanie raportu")
def generate_sales_report(input_data):
    sales_data = input_data["sales_data"]
    date = input_data["date"]
    
    # Tworzenie DataFrame
    df = pd.DataFrame(sales_data)
    
    # Obliczanie wartości sprzedaży
    df["value"] = df["quantity"] * df["price"]
    
    # Obliczanie podsumowania
    total_quantity = df["quantity"].sum()
    total_value = df["value"].sum()
    
    # Tworzenie raportu
    report = {
        "date": date,
        "total_products": len(df),
        "total_quantity": total_quantity,
        "total_value": total_value,
        "products_summary": df.to_dict("records")
    }
    
    return {"report": report}

@task(name="Zapisywanie raportu")
def save_report(input_data, output_dir):
    report = input_data["report"]
    date = report["date"]
    
    # Tworzenie nazwy pliku na podstawie daty
    filename = f"sales_report_{date}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Zapisywanie raportu do pliku
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=4)
    
    return {"report_path": filepath}

@task(name="Wysyłanie powiadomienia")
def send_notification(input_data):
    report = input_data["report"]
    report_path = input_data["report_path"]
    
    # Tworzenie treści powiadomienia
    subject = f"Raport sprzedaży za {report['date']}"
    message = f"""
    Raport sprzedaży za {report['date']}
    
    Podsumowanie:
    - Liczba produktów: {report['total_products']}
    - Łączna ilość: {report['total_quantity']}
    - Łączna wartość: {report['total_value']} PLN
    
    Raport został zapisany w pliku: {report_path}
    """
    
    # Wysyłanie powiadomienia
    from notification_service import send_email_notification
    send_email_notification(subject, message)
    
    return {"notification_sent": True}

# Definicja przepływu DSL
flow_dsl = """
flow DailySalesReport:
    description: "Codzienny raport sprzedaży"
    fetch_sales_data -> generate_sales_report
    generate_sales_report -> save_report
    save_report -> send_notification
"""

# Zapisanie definicji DSL do pliku
with open("dsl_definitions/daily_sales_report.dsl", "w") as f:
    f.write(flow_dsl)

# Utworzenie planera
scheduler = Scheduler()

# Dodanie harmonogramu (codziennie o 8:00)
scheduler.add_schedule(
    "dsl_definitions/daily_sales_report.dsl",
    daily="08:00",
    input_data={
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "output_dir": "reports"
    }
)

# Uruchomienie planera
scheduler.start()
```

Te przykłady pokazują różne zastosowania taskinity, od prostych przepływów sekwencyjnych po zaawansowane scenariusze z równoległym wykonaniem i planowaniem. Możesz je dostosować do swoich potrzeb i używać jako punktu wyjścia do tworzenia własnych przepływów.

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
