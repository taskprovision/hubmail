#!/usr/bin/env python3
"""
Moduł do tworzenia dashboardu webowego dla Taskinity.
Umożliwia zarządzanie przepływami przez interfejs webowy.
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Opcjonalne importy dla Streamlit
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

# Import funkcji z Taskinity
from taskinity.flow_dsl import run_flow_from_dsl, load_dsl, parse_dsl, list_flows
from taskinity.flow_visualizer import generate_mermaid_from_dsl
from taskinity.flow_scheduler import list_schedules, create_schedule, delete_schedule, load_schedule
from taskinity.utils import setup_logger

# Konfiguracja loggera
logger = setup_logger("taskinity.dashboard", level=logging.INFO)

# Ścieżki do katalogów
BASE_DIR = Path(__file__).parent.parent
DSL_DIR = BASE_DIR / "dsl_definitions"
FLOWS_DIR = BASE_DIR / "flows"

# Upewniamy się, że katalogi istnieją
os.makedirs(DSL_DIR, exist_ok=True)
os.makedirs(FLOWS_DIR, exist_ok=True)


def create_dashboard():
    """
    Tworzy dashboard Streamlit dla Taskinity.
    """
    if not STREAMLIT_AVAILABLE:
        logger.error("Streamlit nie jest zainstalowany. Zainstaluj pakiet streamlit, aby korzystać z dashboardu.")
        return
    
    st.set_page_config(
        page_title="Taskinity Dashboard",
        page_icon="🔄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("Taskinity Dashboard")
    st.sidebar.image("https://raw.githubusercontent.com/taskinity/taskinity/main/docs/images/logo.svg", width=200)
    
    menu = st.sidebar.selectbox(
        "Menu",
        ["Przepływy", "Historia", "Harmonogramy", "Nowy przepływ"]
    )
    
    if menu == "Przepływy":
        show_flows_page()
    elif menu == "Historia":
        show_history_page()
    elif menu == "Harmonogramy":
        show_schedules_page()
    elif menu == "Nowy przepływ":
        show_new_flow_page()


def show_flows_page():
    """Wyświetla stronę z listą przepływów."""
    st.header("Przepływy")
    
    # Pobieranie listy plików DSL
    dsl_files = list(DSL_DIR.glob("*.taskinity"))
    
    if not dsl_files:
        st.info("Brak zdefiniowanych przepływów. Utwórz nowy przepływ w zakładce 'Nowy przepływ'.")
        return
    
    # Wyświetlanie listy przepływów
    st.subheader("Dostępne przepływy")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_flow = st.selectbox(
            "Wybierz przepływ",
            [f.stem for f in dsl_files]
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("Uruchom przepływ", key="run_flow"):
            run_selected_flow(selected_flow)
    
    if selected_flow:
        show_flow_details(selected_flow)


def show_flow_details(flow_id: str):
    """
    Wyświetla szczegóły przepływu.
    
    Args:
        flow_id: Identyfikator przepływu
    """
    flow_file = DSL_DIR / f"{flow_id}.taskinity"
    
    if not flow_file.exists():
        st.error(f"Nie znaleziono przepływu: {flow_id}")
        return
    
    # Wczytanie DSL
    dsl_content = load_dsl(str(flow_file))
    flow_def = parse_dsl(dsl_content)
    
    # Wyświetlenie informacji o przepływie
    st.subheader(f"Przepływ: {flow_def.get('name', flow_id)}")
    
    if flow_def.get("description"):
        st.write(flow_def.get("description"))
    
    # Wizualizacja przepływu
    st.subheader("Wizualizacja")
    
    mermaid_code = generate_mermaid_from_dsl(dsl_content)
    st.markdown(f"```mermaid\n{mermaid_code}\n```")
    
    # Zadania w przepływie
    st.subheader("Zadania")
    
    tasks = flow_def.get("tasks", {})
    
    for task_name, task_def in tasks.items():
        with st.expander(f"Zadanie: {task_name}"):
            st.write(f"**Opis:** {task_def.get('description', 'Brak opisu')}")
            st.code(task_def.get("code", ""), language="python")
    
    # Połączenia
    st.subheader("Połączenia")
    
    connections = flow_def.get("connections", [])
    
    for source, target in connections:
        st.write(f"{source} → {target}")
    
    # Opcje
    st.subheader("Opcje")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Edytuj przepływ"):
            st.session_state.edit_flow = flow_id
            st.session_state.edit_dsl = dsl_content
            st.experimental_rerun()
    
    with col2:
        if st.button("Zaplanuj wykonanie"):
            schedule_flow(flow_id)
    
    with col3:
        if st.button("Usuń przepływ"):
            if delete_flow(flow_id):
                st.success(f"Usunięto przepływ: {flow_id}")
                st.experimental_rerun()
            else:
                st.error(f"Nie udało się usunąć przepływu: {flow_id}")


def run_selected_flow(flow_id: str):
    """
    Uruchamia wybrany przepływ.
    
    Args:
        flow_id: Identyfikator przepływu
    """
    flow_file = DSL_DIR / f"{flow_id}.taskinity"
    
    if not flow_file.exists():
        st.error(f"Nie znaleziono przepływu: {flow_id}")
        return
    
    # Wczytanie DSL
    dsl_content = load_dsl(str(flow_file))
    
    # Formularz danych wejściowych
    st.subheader("Dane wejściowe")
    
    with st.form("input_data_form"):
        input_data_json = st.text_area("Dane wejściowe (JSON)", "{}")
        submit_button = st.form_submit_button("Uruchom")
    
    if submit_button:
        try:
            input_data = json.loads(input_data_json)
            
            with st.spinner("Uruchamianie przepływu..."):
                result = run_flow_from_dsl(dsl_content, input_data)
            
            st.success("Przepływ zakończony pomyślnie")
            st.json(result)
        except Exception as e:
            st.error(f"Błąd wykonania przepływu: {str(e)}")


def schedule_flow(flow_id: str):
    """
    Planuje wykonanie przepływu.
    
    Args:
        flow_id: Identyfikator przepływu
    """
    st.subheader("Zaplanuj wykonanie przepływu")
    
    with st.form("schedule_form"):
        schedule_type = st.selectbox(
            "Typ harmonogramu",
            ["interval", "daily", "weekly", "monthly"]
        )
        
        if schedule_type == "interval":
            interval_minutes = st.number_input("Interwał (minuty)", min_value=1, value=60)
            cron_expression = None
        elif schedule_type == "daily":
            interval_minutes = None
            cron_expression = st.text_input("Czas (HH:MM)", "08:00")
        elif schedule_type == "weekly":
            interval_minutes = None
            day_of_week = st.selectbox("Dzień tygodnia", ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"])
            time_of_day = st.text_input("Czas (HH:MM)", "08:00")
            cron_expression = f"{day_of_week}|{time_of_day}"
        elif schedule_type == "monthly":
            interval_minutes = None
            day_of_month = st.number_input("Dzień miesiąca", min_value=1, max_value=31, value=1)
            time_of_day = st.text_input("Czas (HH:MM)", "08:00")
            cron_expression = f"{day_of_month}|{time_of_day}"
        
        description = st.text_input("Opis harmonogramu", f"Harmonogram dla {flow_id}")
        
        input_data_json = st.text_area("Dane wejściowe (JSON)", "{}")
        
        submit_button = st.form_submit_button("Zaplanuj")
    
    if submit_button:
        try:
            input_data = json.loads(input_data_json)
            
            schedule = create_schedule(
                dsl_path=f"{flow_id}.taskinity",
                schedule_type=schedule_type,
                interval_minutes=interval_minutes if interval_minutes else 0,
                cron_expression=cron_expression,
                input_data=input_data,
                description=description
            )
            
            st.success(f"Zaplanowano wykonanie przepływu: {schedule.schedule_id}")
        except Exception as e:
            st.error(f"Błąd planowania przepływu: {str(e)}")


def delete_flow(flow_id: str) -> bool:
    """
    Usuwa przepływ.
    
    Args:
        flow_id: Identyfikator przepływu
        
    Returns:
        True, jeśli usunięto pomyślnie
    """
    flow_file = DSL_DIR / f"{flow_id}.taskinity"
    
    if not flow_file.exists():
        return False
    
    try:
        os.remove(flow_file)
        return True
    except Exception as e:
        logger.error(f"Błąd usuwania przepływu {flow_id}: {str(e)}")
        return False


def show_history_page():
    """Wyświetla stronę z historią wykonania przepływów."""
    st.header("Historia wykonania przepływów")
    
    # Pobieranie historii przepływów
    flows_history = list_flows()
    
    if not flows_history:
        st.info("Brak historii wykonania przepływów.")
        return
    
    # Wyświetlanie historii
    for flow in flows_history:
        flow_id = flow.get("flow_id", "")
        flow_name = flow.get("name", "")
        flow_status = flow.get("status", "")
        flow_time = flow.get("start_time", "")
        
        with st.expander(f"{flow_name} ({flow_id}) - {flow_status} - {flow_time}"):
            st.json(flow)


def show_schedules_page():
    """Wyświetla stronę z harmonogramami."""
    st.header("Harmonogramy")
    
    # Pobieranie harmonogramów
    schedules = list_schedules()
    
    if not schedules:
        st.info("Brak zdefiniowanych harmonogramów.")
        return
    
    # Wyświetlanie harmonogramów
    for schedule_data in schedules:
        schedule_id = schedule_data.get("schedule_id", "")
        dsl_path = schedule_data.get("dsl_path", "")
        schedule_type = schedule_data.get("schedule_type", "")
        next_run = schedule_data.get("next_run", "")
        enabled = "Aktywny" if schedule_data.get("enabled", True) else "Nieaktywny"
        
        with st.expander(f"{dsl_path} ({schedule_id}) - {schedule_type} - {next_run} - {enabled}"):
            st.json(schedule_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Uruchom teraz", key=f"run_{schedule_id}"):
                    schedule = load_schedule(schedule_id)
                    if schedule:
                        with st.spinner("Uruchamianie przepływu..."):
                            result = schedule.run()
                        st.success("Przepływ zakończony pomyślnie")
                        st.json(result)
                    else:
                        st.error(f"Nie znaleziono harmonogramu: {schedule_id}")
            
            with col2:
                if st.button("Usuń harmonogram", key=f"delete_{schedule_id}"):
                    if delete_schedule(schedule_id):
                        st.success(f"Usunięto harmonogram: {schedule_id}")
                        st.experimental_rerun()
                    else:
                        st.error(f"Nie udało się usunąć harmonogramu: {schedule_id}")


def show_new_flow_page():
    """Wyświetla stronę do tworzenia nowego przepływu."""
    st.header("Nowy przepływ")
    
    # Formularz nowego przepływu
    with st.form("new_flow_form"):
        flow_name = st.text_input("Nazwa przepływu")
        flow_id = st.text_input("Identyfikator przepływu (bez spacji, tylko litery, cyfry i podkreślenia)")
        flow_description = st.text_area("Opis przepływu")
        
        dsl_content = st.text_area(
            "Definicja DSL",
            """flow ExampleFlow:
    description: "Przykładowy przepływ"
    
    task Task1:
        description: "Pierwsze zadanie"
        code: |
            print("Wykonuję zadanie 1")
            return {"result": "Wynik zadania 1"}
    
    task Task2:
        description: "Drugie zadanie"
        code: |
            input_data = inputs["Task1"]["result"]
            print(f"Otrzymano dane: {input_data}")
            return {"result": f"Przetworzono: {input_data}"}
    
    Task1 -> Task2
""",
            height=300
        )
        
        submit_button = st.form_submit_button("Utwórz przepływ")
    
    if submit_button:
        if not flow_id:
            st.error("Identyfikator przepływu jest wymagany")
            return
        
        # Walidacja identyfikatora
        if not flow_id.isalnum() and not "_" in flow_id:
            st.error("Identyfikator przepływu może zawierać tylko litery, cyfry i podkreślenia")
            return
        
        # Tworzenie pliku DSL
        flow_file = DSL_DIR / f"{flow_id}.taskinity"
        
        if flow_file.exists():
            st.error(f"Przepływ o identyfikatorze {flow_id} już istnieje")
            return
        
        try:
            # Walidacja DSL
            flow_def = parse_dsl(dsl_content)
            
            # Aktualizacja nazwy i opisu
            if flow_name and flow_name != flow_def.get("name"):
                dsl_content = dsl_content.replace(f"flow {flow_def.get('name', 'ExampleFlow')}:", f"flow {flow_name}:")
            
            if flow_description and flow_description != flow_def.get("description"):
                if "description:" in dsl_content:
                    dsl_content = dsl_content.replace(f'description: "{flow_def.get("description", "")}"', f'description: "{flow_description}"')
                else:
                    lines = dsl_content.split("\n")
                    flow_line_index = -1
                    
                    for i, line in enumerate(lines):
                        if line.strip().startswith("flow ") and line.strip().endswith(":"):
                            flow_line_index = i
                            break
                    
                    if flow_line_index >= 0:
                        lines.insert(flow_line_index + 1, f'    description: "{flow_description}"')
                        dsl_content = "\n".join(lines)
            
            # Zapisanie pliku
            with open(flow_file, "w") as f:
                f.write(dsl_content)
            
            st.success(f"Utworzono przepływ: {flow_id}")
            
            # Przekierowanie do strony przepływów
            st.session_state.menu = "Przepływy"
            st.experimental_rerun()
        
        except Exception as e:
            st.error(f"Błąd tworzenia przepływu: {str(e)}")


def run_dashboard():
    """
    Uruchamia dashboard Streamlit.
    """
    if not STREAMLIT_AVAILABLE:
        logger.error("Streamlit nie jest zainstalowany. Zainstaluj pakiet streamlit, aby korzystać z dashboardu.")
        return
    
    import sys
    
    # Zapisanie tego pliku jako tymczasowego skryptu Streamlit
    dashboard_file = BASE_DIR / "dashboard_app.py"
    
    with open(dashboard_file, "w") as f:
        f.write("""
import os
import sys
from pathlib import Path

# Dodanie katalogu nadrzędnego do ścieżki Pythona
sys.path.insert(0, str(Path(__file__).parent))

# Import modułu dashboard
from taskinity.dashboard import create_dashboard

# Uruchomienie dashboardu
create_dashboard()
        """)
    
    # Uruchomienie Streamlit
    logger.info(f"Uruchamianie dashboardu na http://localhost:8501")
    os.system(f"streamlit run {dashboard_file}")


if __name__ == "__main__":
    run_dashboard()
