#!/usr/bin/env python3
"""
Przykład generowania diagramów Mermaid z przepływów Taskinity.
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Import funkcji z Taskinity
from taskinity import task, flow, run_flow_from_dsl, save_dsl
from taskinity import generate_mermaid_from_dsl, generate_ascii_diagram, visualize_flow

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja ścieżek
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
DSL_DIR = BASE_DIR / "dsl"

# Upewniamy się, że katalogi istnieją
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DSL_DIR, exist_ok=True)

# Przykładowy przepływ do wizualizacji
VISUALIZATION_DEMO_DSL = """
flow VisualizationDemo:
    description: "Przepływ demonstracyjny wizualizacji"
    
    task DataPreparation:
        description: "Przygotowanie danych do wizualizacji"
        code: |
            import random
            import pandas as pd
            from datetime import datetime, timedelta
            
            print("Przygotowanie danych do wizualizacji...")
            
            # Generowanie przykładowych danych
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
            values = [random.randint(10, 100) for _ in range(30)]
            categories = [random.choice(['A', 'B', 'C']) for _ in range(30)]
            
            # Tworzenie DataFrame
            df = pd.DataFrame({
                'date': dates,
                'value': values,
                'category': categories
            })
            
            print(f"Wygenerowano {len(df)} wierszy danych")
            return {"data": df.to_dict('records')}
    
    task GenerateBasicChart:
        description: "Generowanie podstawowego wykresu"
        code: |
            import matplotlib.pyplot as plt
            import pandas as pd
            from pathlib import Path
            
            print("Generowanie podstawowego wykresu...")
            
            # Konwersja danych do DataFrame
            data = inputs["DataPreparation"]["data"]
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            
            # Tworzenie wykresu
            plt.figure(figsize=(10, 6))
            plt.plot(df['date'], df['value'], marker='o')
            plt.title('Podstawowy wykres liniowy')
            plt.xlabel('Data')
            plt.ylabel('Wartość')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Zapisanie wykresu
            output_dir = Path("output")
            os.makedirs(output_dir, exist_ok=True)
            output_file = output_dir / "basic_chart.png"
            plt.savefig(output_file)
            plt.close()
            
            print(f"Zapisano podstawowy wykres do: {output_file}")
            return {"chart_file": str(output_file)}
    
    task GenerateAdvancedChart:
        description: "Generowanie zaawansowanego wykresu"
        code: |
            import matplotlib.pyplot as plt
            import pandas as pd
            import numpy as np
            from pathlib import Path
            
            print("Generowanie zaawansowanego wykresu...")
            
            # Konwersja danych do DataFrame
            data = inputs["DataPreparation"]["data"]
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            
            # Agregacja danych według kategorii
            category_data = df.groupby('category').agg({
                'value': ['mean', 'min', 'max', 'count']
            })
            category_data.columns = ['_'.join(col).strip() for col in category_data.columns.values]
            
            # Tworzenie wykresu
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Wykres 1: Wartości według kategorii
            category_data['value_mean'].plot(kind='bar', ax=ax1, color='skyblue')
            ax1.set_title('Średnia wartość według kategorii')
            ax1.set_xlabel('Kategoria')
            ax1.set_ylabel('Średnia wartość')
            ax1.grid(True, axis='y')
            
            # Wykres 2: Liczba elementów w każdej kategorii
            category_data['value_count'].plot(kind='pie', ax=ax2, autopct='%1.1f%%')
            ax2.set_title('Udział kategorii')
            ax2.set_ylabel('')
            
            plt.tight_layout()
            
            # Zapisanie wykresu
            output_dir = Path("output")
            os.makedirs(output_dir, exist_ok=True)
            output_file = output_dir / "advanced_chart.png"
            plt.savefig(output_file)
            plt.close()
            
            print(f"Zapisano zaawansowany wykres do: {output_file}")
            return {"chart_file": str(output_file)}
    
    task ExportCharts:
        description: "Eksport wykresów do różnych formatów"
        code: |
            import os
            import shutil
            from pathlib import Path
            
            print("Eksport wykresów do różnych formatów...")
            
            basic_chart = inputs["GenerateBasicChart"]["chart_file"]
            advanced_chart = inputs["GenerateAdvancedChart"]["chart_file"]
            
            # Konfiguracja ścieżek
            output_dir = Path("output")
            os.makedirs(output_dir, exist_ok=True)
            
            # Lista formatów do eksportu
            formats = ["png", "svg", "pdf"]
            exported_files = []
            
            # Eksport podstawowego wykresu
            basic_chart_path = Path(basic_chart)
            basic_name = basic_chart_path.stem
            
            # Eksport zaawansowanego wykresu
            advanced_chart_path = Path(advanced_chart)
            advanced_name = advanced_chart_path.stem
            
            # W rzeczywistym przypadku tutaj byłaby konwersja do różnych formatów
            # Dla uproszczenia przykładu, tylko kopiujemy pliki
            for fmt in formats:
                if fmt == "png":
                    # PNG już istnieje
                    exported_files.append(str(basic_chart_path))
                    exported_files.append(str(advanced_chart_path))
                else:
                    # Symulacja eksportu do innych formatów
                    basic_output = output_dir / f"{basic_name}.{fmt}"
                    advanced_output = output_dir / f"{advanced_name}.{fmt}"
                    
                    # Kopiowanie plików (w rzeczywistości byłaby konwersja)
                    shutil.copy(basic_chart_path, basic_output)
                    shutil.copy(advanced_chart_path, advanced_output)
                    
                    exported_files.append(str(basic_output))
                    exported_files.append(str(advanced_output))
            
            print(f"Wyeksportowano wykresy do {len(exported_files)} plików")
            return {"exported_files": exported_files}
    
    DataPreparation -> GenerateBasicChart
    DataPreparation -> GenerateAdvancedChart
    GenerateBasicChart -> ExportCharts
    GenerateAdvancedChart -> ExportCharts
"""

# Zapisanie definicji DSL
def save_dsl_definition():
    """Zapisuje definicję DSL do pliku."""
    dsl_file = DSL_DIR / "visualization_demo.taskinity"
    with open(dsl_file, "w") as f:
        f.write(VISUALIZATION_DEMO_DSL)
    print(f"Zapisano definicję DSL do: {dsl_file}")
    return str(dsl_file)


# Generowanie diagramu Mermaid
def generate_mermaid_diagram():
    """Generuje diagram Mermaid z definicji DSL."""
    print("Generowanie diagramu Mermaid...")
    
    # Generowanie kodu Mermaid
    mermaid_code = generate_mermaid_from_dsl(VISUALIZATION_DEMO_DSL)
    
    # Zapisanie kodu Mermaid
    mermaid_file = OUTPUT_DIR / "visualization_demo.mermaid"
    with open(mermaid_file, "w") as f:
        f.write(mermaid_code)
    
    print(f"Zapisano kod Mermaid do: {mermaid_file}")
    
    # Generowanie diagramu ASCII
    ascii_diagram = generate_ascii_diagram(VISUALIZATION_DEMO_DSL)
    
    # Zapisanie diagramu ASCII
    ascii_file = OUTPUT_DIR / "visualization_demo.txt"
    with open(ascii_file, "w") as f:
        f.write(ascii_diagram)
    
    print(f"Zapisano diagram ASCII do: {ascii_file}")
    
    # Generowanie wizualizacji HTML
    html_file = OUTPUT_DIR / "visualization_demo.html"
    visualize_flow(VISUALIZATION_DEMO_DSL, str(html_file), "html")
    
    print(f"Zapisano wizualizację HTML do: {html_file}")
    
    return {
        "mermaid_file": str(mermaid_file),
        "ascii_file": str(ascii_file),
        "html_file": str(html_file)
    }


if __name__ == "__main__":
    # Zapisanie definicji DSL
    dsl_file = save_dsl_definition()
    
    # Generowanie diagramu Mermaid
    visualization_files = generate_mermaid_diagram()
    
    print("\nWygenerowane pliki wizualizacji:")
    for key, value in visualization_files.items():
        print(f"- {key}: {value}")
    
    # Uruchomienie przepływu (opcjonalnie)
    run_flow = input("\nCzy chcesz uruchomić przepływ? (t/n): ").lower() == 't'
    
    if run_flow:
        print("\nUruchamianie przepływu...")
        result = run_flow_from_dsl(VISUALIZATION_DEMO_DSL)
        
        print("\nWynik przepływu:")
        print(f"- Podstawowy wykres: {result['GenerateBasicChart']['chart_file']}")
        print(f"- Zaawansowany wykres: {result['GenerateAdvancedChart']['chart_file']}")
        print(f"- Wyeksportowane pliki: {', '.join(result['ExportCharts']['exported_files'])}")
    
    print("\nZakończono generowanie wizualizacji.")
