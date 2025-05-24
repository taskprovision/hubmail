#!/usr/bin/env python3
"""
Moduł zawierający przykłady i szablony przepływów Taskinity.
Umożliwia szybkie rozpoczęcie pracy z Taskinity poprzez gotowe przykłady.
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Ścieżki do katalogów
BASE_DIR = Path(__file__).parent.parent
EXAMPLES_DIR = BASE_DIR / "examples"
TEMPLATES_DIR = BASE_DIR / "templates"

# Upewniamy się, że katalogi istnieją
os.makedirs(EXAMPLES_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Przykładowe przepływy
EXAMPLE_FLOWS = {
    "hello_world": {
        "name": "Hello World",
        "description": "Prosty przepływ demonstracyjny",
        "dsl": """
flow HelloWorld:
    description: "Prosty przepływ demonstracyjny"
    
    task SayHello:
        description: "Wyświetla powitanie"
        code: |
            print("Witaj w Taskinity!")
            return {"message": "Hello World"}
    
    task ProcessMessage:
        description: "Przetwarza wiadomość"
        code: |
            message = inputs["SayHello"]["message"]
            processed = message.upper()
            print(f"Przetworzona wiadomość: {processed}")
            return {"processed_message": processed}
    
    task FinalizeFlow:
        description: "Finalizuje przepływ"
        code: |
            message = inputs["ProcessMessage"]["processed_message"]
            print(f"Finalizacja przepływu z wiadomością: {message}")
            return {"final_message": f"Zakończono przepływ: {message}"}
    
    SayHello -> ProcessMessage -> FinalizeFlow
"""
    },
    
    "data_processing": {
        "name": "Przetwarzanie Danych",
        "description": "Przykład przetwarzania danych z wykorzystaniem pandas",
        "dsl": """
flow DataProcessing:
    description: "Przykład przetwarzania danych"
    
    task LoadData:
        description: "Ładuje dane z pliku CSV"
        code: |
            import pandas as pd
            
            # Przykładowe dane
            data = {
                'Imię': ['Jan', 'Anna', 'Piotr', 'Maria', 'Krzysztof'],
                'Wiek': [28, 34, 42, 31, 39],
                'Miasto': ['Warszawa', 'Kraków', 'Gdańsk', 'Poznań', 'Wrocław']
            }
            
            df = pd.DataFrame(data)
            print(f"Załadowano dane: {len(df)} wierszy")
            
            return {"data": df.to_dict()}
    
    task ProcessData:
        description: "Przetwarza dane"
        code: |
            import pandas as pd
            
            # Konwersja z powrotem do DataFrame
            data = inputs["LoadData"]["data"]
            df = pd.DataFrame(data)
            
            # Przykładowe przetwarzanie
            df['Kategoria'] = df['Wiek'].apply(lambda x: 'Młody' if x < 35 else 'Dojrzały')
            
            print(f"Przetworzono dane, dodano kolumnę 'Kategoria'")
            
            return {"processed_data": df.to_dict()}
    
    task AnalyzeData:
        description: "Analizuje przetworzone dane"
        code: |
            import pandas as pd
            
            # Konwersja z powrotem do DataFrame
            data = inputs["ProcessData"]["processed_data"]
            df = pd.DataFrame(data)
            
            # Przykładowa analiza
            summary = {
                'liczba_rekordów': len(df),
                'średni_wiek': df['Wiek'].mean(),
                'kategorie': df['Kategoria'].value_counts().to_dict()
            }
            
            print(f"Analiza danych: {summary}")
            
            return {"summary": summary}
    
    LoadData -> ProcessData -> AnalyzeData
"""
    },
    
    "api_integration": {
        "name": "Integracja API",
        "description": "Przykład integracji z zewnętrznym API",
        "dsl": """
flow APIIntegration:
    description: "Przykład integracji z zewnętrznym API"
    
    task FetchData:
        description: "Pobiera dane z API"
        code: |
            import requests
            
            url = "https://jsonplaceholder.typicode.com/posts"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Pobrano {len(data)} rekordów z API")
                return {"data": data[:5]}  # Zwracamy tylko 5 pierwszych rekordów dla przykładu
            else:
                print(f"Błąd pobierania danych: {response.status_code}")
                return {"error": f"HTTP Error: {response.status_code}"}
    
    task ProcessAPIData:
        description: "Przetwarza dane z API"
        code: |
            data = inputs["FetchData"].get("data", [])
            
            if not data:
                error = inputs["FetchData"].get("error", "Nieznany błąd")
                print(f"Nie można przetworzyć danych: {error}")
                return {"error": error}
            
            # Przykładowe przetwarzanie
            processed_data = []
            for item in data:
                processed_data.append({
                    "id": item["id"],
                    "title": item["title"],
                    "title_length": len(item["title"]),
                    "body_preview": item["body"][:50] + "..."
                })
            
            print(f"Przetworzono {len(processed_data)} rekordów")
            return {"processed_data": processed_data}
    
    task SaveResults:
        description: "Zapisuje wyniki"
        code: |
            import json
            
            if "error" in inputs["ProcessAPIData"]:
                print(f"Nie można zapisać wyników: {inputs['ProcessAPIData']['error']}")
                return {"status": "error"}
            
            data = inputs["ProcessAPIData"]["processed_data"]
            
            # W rzeczywistym przypadku można zapisać do bazy danych lub pliku
            print(f"Zapisywanie {len(data)} rekordów")
            print(json.dumps(data, indent=2))
            
            return {"status": "success", "count": len(data)}
    
    FetchData -> ProcessAPIData -> SaveResults
"""
    },
    
    "parallel_tasks": {
        "name": "Zadania Równoległe",
        "description": "Przykład przepływu z równoległymi zadaniami",
        "dsl": """
flow ParallelTasks:
    description: "Przykład przepływu z równoległymi zadaniami"
    
    task Start:
        description: "Inicjalizuje przepływ"
        code: |
            import random
            
            # Generowanie przykładowych danych
            data = [random.randint(1, 100) for _ in range(20)]
            
            print(f"Wygenerowano dane: {data}")
            return {"data": data}
    
    task CalculateSum:
        description: "Oblicza sumę"
        code: |
            data = inputs["Start"]["data"]
            result = sum(data)
            
            print(f"Suma: {result}")
            return {"sum": result}
    
    task CalculateAverage:
        description: "Oblicza średnią"
        code: |
            data = inputs["Start"]["data"]
            result = sum(data) / len(data)
            
            print(f"Średnia: {result}")
            return {"average": result}
    
    task FindMinMax:
        description: "Znajduje wartości min i max"
        code: |
            data = inputs["Start"]["data"]
            min_val = min(data)
            max_val = max(data)
            
            print(f"Min: {min_val}, Max: {max_val}")
            return {"min": min_val, "max": max_val}
    
    task Summarize:
        description: "Podsumowuje wyniki"
        code: |
            summary = {
                "sum": inputs["CalculateSum"]["sum"],
                "average": inputs["CalculateAverage"]["average"],
                "min": inputs["FindMinMax"]["min"],
                "max": inputs["FindMinMax"]["max"]
            }
            
            print(f"Podsumowanie: {summary}")
            return {"summary": summary}
    
    Start -> CalculateSum
    Start -> CalculateAverage
    Start -> FindMinMax
    CalculateSum -> Summarize
    CalculateAverage -> Summarize
    FindMinMax -> Summarize
"""
    }
}

# Szablony przepływów
FLOW_TEMPLATES = {
    "basic": {
        "name": "Podstawowy Przepływ",
        "description": "Szablon podstawowego przepływu",
        "dsl": """
flow BasicFlow:
    description: "Podstawowy przepływ"
    
    task Task1:
        description: "Pierwsze zadanie"
        code: |
            # Tutaj umieść kod pierwszego zadania
            return {"result": "Wynik zadania 1"}
    
    task Task2:
        description: "Drugie zadanie"
        code: |
            # Tutaj umieść kod drugiego zadania
            input_data = inputs["Task1"]["result"]
            return {"result": f"Przetworzono: {input_data}"}
    
    task Task3:
        description: "Trzecie zadanie"
        code: |
            # Tutaj umieść kod trzeciego zadania
            input_data = inputs["Task2"]["result"]
            return {"result": f"Finalizacja: {input_data}"}
    
    Task1 -> Task2 -> Task3
"""
    },
    
    "data_pipeline": {
        "name": "Potok Przetwarzania Danych",
        "description": "Szablon potoku przetwarzania danych",
        "dsl": """
flow DataPipeline:
    description: "Potok przetwarzania danych"
    
    task LoadData:
        description: "Ładowanie danych"
        code: |
            # Tutaj umieść kod ładowania danych
            # np. z pliku CSV, bazy danych, API
            return {"data": [/* dane */]}
    
    task CleanData:
        description: "Czyszczenie danych"
        code: |
            data = inputs["LoadData"]["data"]
            # Tutaj umieść kod czyszczenia danych
            return {"cleaned_data": data}
    
    task TransformData:
        description: "Transformacja danych"
        code: |
            data = inputs["CleanData"]["cleaned_data"]
            # Tutaj umieść kod transformacji danych
            return {"transformed_data": data}
    
    task AnalyzeData:
        description: "Analiza danych"
        code: |
            data = inputs["TransformData"]["transformed_data"]
            # Tutaj umieść kod analizy danych
            return {"results": {/* wyniki analizy */}}
    
    task SaveResults:
        description: "Zapisywanie wyników"
        code: |
            results = inputs["AnalyzeData"]["results"]
            # Tutaj umieść kod zapisywania wyników
            return {"status": "success"}
    
    LoadData -> CleanData -> TransformData -> AnalyzeData -> SaveResults
"""
    },
    
    "api_workflow": {
        "name": "Przepływ API",
        "description": "Szablon przepływu integracji API",
        "dsl": """
flow APIWorkflow:
    description: "Przepływ integracji API"
    
    task FetchData:
        description: "Pobieranie danych z API"
        code: |
            import requests
            
            # Tutaj umieść kod pobierania danych z API
            url = "https://api.example.com/data"
            # response = requests.get(url)
            # data = response.json()
            
            # Dla przykładu
            data = [/* przykładowe dane */]
            
            return {"data": data}
    
    task ProcessData:
        description: "Przetwarzanie danych"
        code: |
            data = inputs["FetchData"]["data"]
            # Tutaj umieść kod przetwarzania danych
            return {"processed_data": data}
    
    task PostResults:
        description: "Wysyłanie wyników do API"
        code: |
            import requests
            
            data = inputs["ProcessData"]["processed_data"]
            # Tutaj umieść kod wysyłania danych do API
            url = "https://api.example.com/results"
            # response = requests.post(url, json=data)
            
            return {"status": "success"}
    
    FetchData -> ProcessData -> PostResults
"""
    },
    
    "scheduled_task": {
        "name": "Zadanie Harmonogramu",
        "description": "Szablon zadania uruchamianego według harmonogramu",
        "dsl": """
flow ScheduledTask:
    description: "Zadanie uruchamiane według harmonogramu"
    
    task CheckSchedule:
        description: "Sprawdzanie harmonogramu"
        code: |
            import datetime
            
            now = datetime.datetime.now()
            schedule_info = {
                "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "day_of_week": now.strftime("%A"),
                "is_weekend": now.weekday() >= 5
            }
            
            print(f"Czas wykonania: {schedule_info['current_time']}")
            return {"schedule_info": schedule_info}
    
    task ExecuteTask:
        description: "Wykonanie zadania"
        code: |
            schedule_info = inputs["CheckSchedule"]["schedule_info"]
            
            # Tutaj umieść kod zadania do wykonania
            print(f"Wykonywanie zadania o {schedule_info['current_time']}")
            
            return {"status": "completed", "execution_time": schedule_info["current_time"]}
    
    task LogResults:
        description: "Logowanie wyników"
        code: |
            import datetime
            
            execution_info = inputs["ExecuteTask"]
            end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = {
                "task": "ScheduledTask",
                "status": execution_info["status"],
                "start_time": execution_info["execution_time"],
                "end_time": end_time
            }
            
            print(f"Log: {log_entry}")
            return {"log": log_entry}
    
    CheckSchedule -> ExecuteTask -> LogResults
"""
    }
}

def list_examples() -> List[Dict[str, str]]:
    """
    Zwraca listę dostępnych przykładów.
    
    Returns:
        Lista przykładów z ID, nazwą i opisem
    """
    return [
        {"id": example_id, "name": example["name"], "description": example["description"]}
        for example_id, example in EXAMPLE_FLOWS.items()
    ]

def list_templates() -> List[Dict[str, str]]:
    """
    Zwraca listę dostępnych szablonów.
    
    Returns:
        Lista szablonów z ID, nazwą i opisem
    """
    return [
        {"id": template_id, "name": template["name"], "description": template["description"]}
        for template_id, template in FLOW_TEMPLATES.items()
    ]

def get_example(example_id: str) -> Optional[Dict[str, Any]]:
    """
    Zwraca przykład o podanym ID.
    
    Args:
        example_id: ID przykładu
        
    Returns:
        Przykład lub None, jeśli nie znaleziono
    """
    return EXAMPLE_FLOWS.get(example_id)

def get_template(template_id: str) -> Optional[Dict[str, Any]]:
    """
    Zwraca szablon o podanym ID.
    
    Args:
        template_id: ID szablonu
        
    Returns:
        Szablon lub None, jeśli nie znaleziono
    """
    return FLOW_TEMPLATES.get(template_id)

def save_example_to_file(example_id: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Zapisuje przykład do pliku.
    
    Args:
        example_id: ID przykładu
        output_path: Ścieżka do pliku wyjściowego (opcjonalnie)
        
    Returns:
        Ścieżka do zapisanego pliku lub None, jeśli wystąpił błąd
    """
    example = get_example(example_id)
    if not example:
        return None
    
    if not output_path:
        output_path = os.path.join(EXAMPLES_DIR, f"{example_id}.taskinity")
    
    try:
        with open(output_path, "w") as f:
            f.write(example["dsl"].strip())
        return output_path
    except Exception as e:
        print(f"Błąd zapisywania przykładu: {str(e)}")
        return None

def save_template_to_file(template_id: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Zapisuje szablon do pliku.
    
    Args:
        template_id: ID szablonu
        output_path: Ścieżka do pliku wyjściowego (opcjonalnie)
        
    Returns:
        Ścieżka do zapisanego pliku lub None, jeśli wystąpił błąd
    """
    template = get_template(template_id)
    if not template:
        return None
    
    if not output_path:
        output_path = os.path.join(TEMPLATES_DIR, f"{template_id}.taskinity")
    
    try:
        with open(output_path, "w") as f:
            f.write(template["dsl"].strip())
        return output_path
    except Exception as e:
        print(f"Błąd zapisywania szablonu: {str(e)}")
        return None

def create_examples_directory():
    """Tworzy katalog przykładów z wszystkimi przykładami."""
    os.makedirs(EXAMPLES_DIR, exist_ok=True)
    
    for example_id in EXAMPLE_FLOWS:
        save_example_to_file(example_id)
    
    print(f"Utworzono katalog przykładów: {EXAMPLES_DIR}")

def create_templates_directory():
    """Tworzy katalog szablonów z wszystkimi szablonami."""
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    
    for template_id in FLOW_TEMPLATES:
        save_template_to_file(template_id)
    
    print(f"Utworzono katalog szablonów: {TEMPLATES_DIR}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Użycie: python examples.py [list-examples|list-templates|get-example|get-template|create-examples|create-templates]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list-examples":
        examples = list_examples()
        print(f"Dostępne przykłady ({len(examples)}):")
        for example in examples:
            print(f"- {example['id']}: {example['name']} - {example['description']}")
    
    elif command == "list-templates":
        templates = list_templates()
        print(f"Dostępne szablony ({len(templates)}):")
        for template in templates:
            print(f"- {template['id']}: {template['name']} - {template['description']}")
    
    elif command == "get-example" and len(sys.argv) >= 3:
        example_id = sys.argv[2]
        output_path = sys.argv[3] if len(sys.argv) > 3 else None
        
        result = save_example_to_file(example_id, output_path)
        if result:
            print(f"Zapisano przykład do pliku: {result}")
        else:
            print(f"Nie znaleziono przykładu: {example_id}")
    
    elif command == "get-template" and len(sys.argv) >= 3:
        template_id = sys.argv[2]
        output_path = sys.argv[3] if len(sys.argv) > 3 else None
        
        result = save_template_to_file(template_id, output_path)
        if result:
            print(f"Zapisano szablon do pliku: {result}")
        else:
            print(f"Nie znaleziono szablonu: {template_id}")
    
    elif command == "create-examples":
        create_examples_directory()
    
    elif command == "create-templates":
        create_templates_directory()
    
    else:
        print("Nieznane polecenie lub brak wymaganych parametrów")
        print("Użycie: python examples.py [list-examples|list-templates|get-example|get-template|create-examples|create-templates]")
