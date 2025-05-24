#!/usr/bin/env python3
"""
Przykład przetwarzania danych CSV z wykorzystaniem Taskinity.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from dotenv import load_dotenv

# Import funkcji z Taskinity
from taskinity import task, flow, run_flow_from_dsl, save_dsl

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja ścieżek
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
DSL_DIR = BASE_DIR / "dsl"

# Upewniamy się, że katalogi istnieją
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DSL_DIR, exist_ok=True)

# Przykładowe dane CSV (jeśli nie istnieją)
SAMPLE_CSV = DATA_DIR / "sample_data.csv"
if not SAMPLE_CSV.exists():
    # Tworzenie przykładowych danych
    import numpy as np
    
    # Generowanie danych
    np.random.seed(42)
    dates = pd.date_range('20230101', periods=100)
    data = {
        'date': dates,
        'value': np.random.randn(100).cumsum() + 100,
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'quantity': np.random.randint(1, 100, 100)
    }
    
    # Zapisanie do CSV
    df = pd.DataFrame(data)
    df.to_csv(SAMPLE_CSV, index=False)
    print(f"Utworzono przykładowe dane: {SAMPLE_CSV}")


# Definicja zadań
@task(name="LoadCSVData", description="Ładuje dane z pliku CSV")
def load_csv_data(file_path):
    """Ładuje dane z pliku CSV."""
    print(f"Ładowanie danych z: {file_path}")
    df = pd.read_csv(file_path)
    print(f"Załadowano {len(df)} wierszy danych")
    return {"data": df.to_dict('records')}


@task(name="CleanData", description="Czyści i przetwarza dane")
def clean_data(inputs):
    """Czyści i przetwarza dane."""
    # Konwersja z powrotem do DataFrame
    data = inputs["LoadCSVData"]["data"]
    df = pd.DataFrame(data)
    
    # Czyszczenie danych
    print("Czyszczenie danych...")
    
    # Usuwanie duplikatów
    df = df.drop_duplicates()
    
    # Konwersja dat
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    # Obsługa brakujących wartości
    df = df.fillna({
        'value': df['value'].mean(),
        'category': 'Unknown',
        'quantity': 0
    })
    
    print(f"Po czyszczeniu: {len(df)} wierszy")
    return {"cleaned_data": df.to_dict('records')}


@task(name="TransformData", description="Transformuje dane do analizy")
def transform_data(inputs):
    """Transformuje dane do analizy."""
    # Konwersja z powrotem do DataFrame
    data = inputs["CleanData"]["cleaned_data"]
    df = pd.DataFrame(data)
    
    print("Transformacja danych...")
    
    # Dodanie nowych kolumn
    if 'quantity' in df.columns and 'value' in df.columns:
        df['total_value'] = df['quantity'] * df['value']
    
    # Kategoryzacja wartości
    if 'value' in df.columns:
        df['value_category'] = pd.cut(
            df['value'],
            bins=[-float('inf'), 90, 100, 110, float('inf')],
            labels=['Low', 'Medium', 'High', 'Very High']
        )
    
    # Agregacja według kategorii
    if 'category' in df.columns:
        category_stats = df.groupby('category').agg({
            'value': ['mean', 'min', 'max'],
            'quantity': 'sum'
        })
        category_stats.columns = ['_'.join(col).strip() for col in category_stats.columns.values]
        category_stats = category_stats.reset_index()
    else:
        category_stats = pd.DataFrame()
    
    print("Transformacja zakończona")
    return {
        "transformed_data": df.to_dict('records'),
        "category_stats": category_stats.to_dict('records') if not category_stats.empty else []
    }


@task(name="AnalyzeData", description="Analizuje dane")
def analyze_data(inputs):
    """Analizuje dane."""
    # Konwersja z powrotem do DataFrame
    data = inputs["TransformData"]["transformed_data"]
    df = pd.DataFrame(data)
    
    category_stats = inputs["TransformData"]["category_stats"]
    category_stats_df = pd.DataFrame(category_stats) if category_stats else pd.DataFrame()
    
    print("Analiza danych...")
    
    # Podstawowe statystyki
    basic_stats = {
        'count': len(df),
        'value_mean': df['value'].mean() if 'value' in df.columns else None,
        'value_std': df['value'].std() if 'value' in df.columns else None,
        'quantity_total': df['quantity'].sum() if 'quantity' in df.columns else None,
        'total_value': df['total_value'].sum() if 'total_value' in df.columns else None
    }
    
    # Analiza trendów (jeśli są daty)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Analiza miesięczna
        df['month'] = df['date'].dt.to_period('M')
        monthly_data = df.groupby('month').agg({
            'value': 'mean',
            'quantity': 'sum',
            'total_value': 'sum'
        }).reset_index()
        monthly_data['month'] = monthly_data['month'].astype(str)
    else:
        monthly_data = pd.DataFrame()
    
    print("Analiza zakończona")
    return {
        "basic_stats": basic_stats,
        "monthly_data": monthly_data.to_dict('records') if not monthly_data.empty else [],
        "category_stats": category_stats
    }


@task(name="GenerateReport", description="Generuje raport i wizualizacje")
def generate_report(inputs):
    """Generuje raport i wizualizacje."""
    basic_stats = inputs["AnalyzeData"]["basic_stats"]
    monthly_data = inputs["AnalyzeData"]["monthly_data"]
    category_stats = inputs["AnalyzeData"]["category_stats"]
    
    print("Generowanie raportu...")
    
    # Tworzenie raportu tekstowego
    report_file = OUTPUT_DIR / "report.txt"
    with open(report_file, "w") as f:
        f.write("=== RAPORT ANALIZY DANYCH ===\n\n")
        
        f.write("Podstawowe statystyki:\n")
        for key, value in basic_stats.items():
            if value is not None:
                f.write(f"- {key}: {value}\n")
        
        if category_stats:
            f.write("\nStatystyki według kategorii:\n")
            for stat in category_stats:
                f.write(f"- Kategoria: {stat.get('category')}\n")
                for key, value in stat.items():
                    if key != 'category':
                        f.write(f"  - {key}: {value}\n")
    
    # Tworzenie wizualizacji
    if monthly_data:
        # Konwersja do DataFrame
        monthly_df = pd.DataFrame(monthly_data)
        
        # Wykres trendu wartości
        plt.figure(figsize=(10, 6))
        plt.plot(monthly_df['month'], monthly_df['value'], marker='o')
        plt.title('Trend średniej wartości w czasie')
        plt.xlabel('Miesiąc')
        plt.ylabel('Średnia wartość')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "value_trend.png")
        plt.close()
        
        # Wykres ilości
        plt.figure(figsize=(10, 6))
        plt.bar(monthly_df['month'], monthly_df['quantity'])
        plt.title('Suma ilości w czasie')
        plt.xlabel('Miesiąc')
        plt.ylabel('Suma ilości')
        plt.grid(True, axis='y')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "quantity_trend.png")
        plt.close()
    
    if category_stats:
        # Konwersja do DataFrame
        category_df = pd.DataFrame(category_stats)
        
        # Wykres wartości według kategorii
        if 'value_mean' in category_df.columns:
            plt.figure(figsize=(10, 6))
            plt.bar(category_df['category'], category_df['value_mean'])
            plt.title('Średnia wartość według kategorii')
            plt.xlabel('Kategoria')
            plt.ylabel('Średnia wartość')
            plt.grid(True, axis='y')
            plt.tight_layout()
            plt.savefig(OUTPUT_DIR / "category_values.png")
            plt.close()
    
    print(f"Raport zapisany do: {report_file}")
    print(f"Wizualizacje zapisane w katalogu: {OUTPUT_DIR}")
    
    return {
        "report_file": str(report_file),
        "visualization_dir": str(OUTPUT_DIR)
    }


# Definicja przepływu
@flow(name="CSVDataProcessingFlow", description="Przepływ przetwarzania danych CSV")
def csv_data_processing_flow():
    # Definicja zadań
    load_data = load_csv_data(str(SAMPLE_CSV))
    clean = clean_data({"LoadCSVData": load_data})
    transform = transform_data({"CleanData": clean})
    analyze = analyze_data({"TransformData": transform})
    report = generate_report({"AnalyzeData": analyze})
    
    # Definicja przepływu
    return {
        "tasks": {
            "LoadCSVData": load_data,
            "CleanData": clean,
            "TransformData": transform,
            "AnalyzeData": analyze,
            "GenerateReport": report
        },
        "connections": [
            ("LoadCSVData", "CleanData"),
            ("CleanData", "TransformData"),
            ("TransformData", "AnalyzeData"),
            ("AnalyzeData", "GenerateReport")
        ]
    }


# Definicja przepływu w DSL
CSV_PROCESSING_DSL = """
flow CSVDataProcessing:
    description: "Przepływ przetwarzania danych CSV"
    
    task LoadCSVData:
        description: "Ładuje dane z pliku CSV"
        code: |
            import pandas as pd
            
            file_path = inputs.get("file_path", "data/sample_data.csv")
            print(f"Ładowanie danych z: {file_path}")
            
            df = pd.read_csv(file_path)
            print(f"Załadowano {len(df)} wierszy danych")
            
            return {"data": df.to_dict('records')}
    
    task CleanData:
        description: "Czyści i przetwarza dane"
        code: |
            import pandas as pd
            
            # Konwersja z powrotem do DataFrame
            data = inputs["LoadCSVData"]["data"]
            df = pd.DataFrame(data)
            
            # Czyszczenie danych
            print("Czyszczenie danych...")
            
            # Usuwanie duplikatów
            df = df.drop_duplicates()
            
            # Konwersja dat
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            
            # Obsługa brakujących wartości
            df = df.fillna({
                'value': df['value'].mean(),
                'category': 'Unknown',
                'quantity': 0
            })
            
            print(f"Po czyszczeniu: {len(df)} wierszy")
            return {"cleaned_data": df.to_dict('records')}
    
    task TransformData:
        description: "Transformuje dane do analizy"
        code: |
            import pandas as pd
            
            # Konwersja z powrotem do DataFrame
            data = inputs["CleanData"]["cleaned_data"]
            df = pd.DataFrame(data)
            
            print("Transformacja danych...")
            
            # Dodanie nowych kolumn
            if 'quantity' in df.columns and 'value' in df.columns:
                df['total_value'] = df['quantity'] * df['value']
            
            # Kategoryzacja wartości
            if 'value' in df.columns:
                df['value_category'] = pd.cut(
                    df['value'],
                    bins=[-float('inf'), 90, 100, 110, float('inf')],
                    labels=['Low', 'Medium', 'High', 'Very High']
                )
            
            # Agregacja według kategorii
            if 'category' in df.columns:
                category_stats = df.groupby('category').agg({
                    'value': ['mean', 'min', 'max'],
                    'quantity': 'sum'
                })
                category_stats.columns = ['_'.join(col).strip() for col in category_stats.columns.values]
                category_stats = category_stats.reset_index()
            else:
                category_stats = pd.DataFrame()
            
            print("Transformacja zakończona")
            return {
                "transformed_data": df.to_dict('records'),
                "category_stats": category_stats.to_dict('records') if not category_stats.empty else []
            }
    
    task AnalyzeData:
        description: "Analizuje dane"
        code: |
            import pandas as pd
            
            # Konwersja z powrotem do DataFrame
            data = inputs["TransformData"]["transformed_data"]
            df = pd.DataFrame(data)
            
            category_stats = inputs["TransformData"]["category_stats"]
            category_stats_df = pd.DataFrame(category_stats) if category_stats else pd.DataFrame()
            
            print("Analiza danych...")
            
            # Podstawowe statystyki
            basic_stats = {
                'count': len(df),
                'value_mean': df['value'].mean() if 'value' in df.columns else None,
                'value_std': df['value'].std() if 'value' in df.columns else None,
                'quantity_total': df['quantity'].sum() if 'quantity' in df.columns else None,
                'total_value': df['total_value'].sum() if 'total_value' in df.columns else None
            }
            
            # Analiza trendów (jeśli są daty)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                
                # Analiza miesięczna
                df['month'] = df['date'].dt.to_period('M')
                monthly_data = df.groupby('month').agg({
                    'value': 'mean',
                    'quantity': 'sum',
                    'total_value': 'sum'
                }).reset_index()
                monthly_data['month'] = monthly_data['month'].astype(str)
            else:
                monthly_data = pd.DataFrame()
            
            print("Analiza zakończona")
            return {
                "basic_stats": basic_stats,
                "monthly_data": monthly_data.to_dict('records') if not monthly_data.empty else [],
                "category_stats": category_stats
            }
    
    task GenerateReport:
        description: "Generuje raport i wizualizacje"
        code: |
            import os
            import pandas as pd
            import matplotlib.pyplot as plt
            from pathlib import Path
            
            basic_stats = inputs["AnalyzeData"]["basic_stats"]
            monthly_data = inputs["AnalyzeData"]["monthly_data"]
            category_stats = inputs["AnalyzeData"]["category_stats"]
            
            print("Generowanie raportu...")
            
            # Konfiguracja ścieżek
            OUTPUT_DIR = Path("output")
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # Tworzenie raportu tekstowego
            report_file = OUTPUT_DIR / "report.txt"
            with open(report_file, "w") as f:
                f.write("=== RAPORT ANALIZY DANYCH ===\\n\\n")
                
                f.write("Podstawowe statystyki:\\n")
                for key, value in basic_stats.items():
                    if value is not None:
                        f.write(f"- {key}: {value}\\n")
                
                if category_stats:
                    f.write("\\nStatystyki według kategorii:\\n")
                    for stat in category_stats:
                        f.write(f"- Kategoria: {stat.get('category')}\\n")
                        for key, value in stat.items():
                            if key != 'category':
                                f.write(f"  - {key}: {value}\\n")
            
            # Tworzenie wizualizacji
            if monthly_data:
                # Konwersja do DataFrame
                monthly_df = pd.DataFrame(monthly_data)
                
                # Wykres trendu wartości
                plt.figure(figsize=(10, 6))
                plt.plot(monthly_df['month'], monthly_df['value'], marker='o')
                plt.title('Trend średniej wartości w czasie')
                plt.xlabel('Miesiąc')
                plt.ylabel('Średnia wartość')
                plt.grid(True)
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(OUTPUT_DIR / "value_trend.png")
                plt.close()
                
                # Wykres ilości
                plt.figure(figsize=(10, 6))
                plt.bar(monthly_df['month'], monthly_df['quantity'])
                plt.title('Suma ilości w czasie')
                plt.xlabel('Miesiąc')
                plt.ylabel('Suma ilości')
                plt.grid(True, axis='y')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(OUTPUT_DIR / "quantity_trend.png")
                plt.close()
            
            if category_stats:
                # Konwersja do DataFrame
                category_df = pd.DataFrame(category_stats)
                
                # Wykres wartości według kategorii
                if 'value_mean' in category_df.columns:
                    plt.figure(figsize=(10, 6))
                    plt.bar(category_df['category'], category_df['value_mean'])
                    plt.title('Średnia wartość według kategorii')
                    plt.xlabel('Kategoria')
                    plt.ylabel('Średnia wartość')
                    plt.grid(True, axis='y')
                    plt.tight_layout()
                    plt.savefig(OUTPUT_DIR / "category_values.png")
                    plt.close()
            
            print(f"Raport zapisany do: {report_file}")
            print(f"Wizualizacje zapisane w katalogu: {OUTPUT_DIR}")
            
            return {
                "report_file": str(report_file),
                "visualization_dir": str(OUTPUT_DIR)
            }
    
    LoadCSVData -> CleanData -> TransformData -> AnalyzeData -> GenerateReport
"""

# Zapisanie definicji DSL
def save_dsl_definition():
    """Zapisuje definicję DSL do pliku."""
    dsl_file = DSL_DIR / "csv_processing.taskinity"
    with open(dsl_file, "w") as f:
        f.write(CSV_PROCESSING_DSL)
    print(f"Zapisano definicję DSL do: {dsl_file}")
    return str(dsl_file)


if __name__ == "__main__":
    # Zapisanie definicji DSL
    dsl_file = save_dsl_definition()
    
    # Uruchomienie przepływu z definicji DSL
    print("\nUruchamianie przepływu z definicji DSL...")
    result = run_flow_from_dsl(
        CSV_PROCESSING_DSL,
        {"file_path": str(SAMPLE_CSV)}
    )
    
    print("\nWynik przepływu:")
    print(f"- Raport: {result['GenerateReport']['report_file']}")
    print(f"- Wizualizacje: {result['GenerateReport']['visualization_dir']}")
    
    print("\nZakończono przetwarzanie danych CSV.")
