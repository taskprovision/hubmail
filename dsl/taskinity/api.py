#!/usr/bin/env python3
"""
Moduł do integracji Taskinity z API.
Umożliwia udostępnianie przepływów jako endpointów API.
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime

# Opcjonalne importy dla FastAPI
try:
    from fastapi import FastAPI, HTTPException, Body, Depends, Query, Path as PathParam
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Tworzymy zastępcze klasy, aby kod się kompilował
    class BaseModel:
        pass
    
    class Field:
        def __init__(self, *args, **kwargs):
            pass

# Import funkcji z Taskinity
from taskinity.core.taskinity_core import run_flow_from_dsl, load_dsl, parse_dsl, list_flows
from taskinity.utils import generate_id, timed_execution, setup_logger

# Konfiguracja loggera
logger = setup_logger("taskinity.api", level=logging.INFO)

# Ścieżki do katalogów
BASE_DIR = Path(__file__).parent.parent
DSL_DIR = BASE_DIR / "dsl_definitions"
API_CONFIG_FILE = BASE_DIR / "config" / "api_config.json"

# Upewniamy się, że katalogi istnieją
os.makedirs(DSL_DIR, exist_ok=True)
os.makedirs(API_CONFIG_FILE.parent, exist_ok=True)

# Domyślna konfiguracja API
DEFAULT_API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": False,
    "allowed_origins": ["*"],
    "api_prefix": "/api/v1",
    "require_auth": False,
    "auth_token": "",
    "exposed_flows": []
}


# Modele danych dla API (jeśli FastAPI jest dostępne)
if FASTAPI_AVAILABLE:
    class FlowInput(BaseModel):
        """Model danych wejściowych dla przepływu."""
        flow_id: Optional[str] = Field(None, description="Identyfikator przepływu")
        inputs: Dict[str, Any] = Field(default_factory=dict, description="Dane wejściowe dla przepływu")
    
    class FlowOutput(BaseModel):
        """Model danych wyjściowych dla przepływu."""
        flow_id: str = Field(..., description="Identyfikator przepływu")
        status: str = Field(..., description="Status wykonania przepływu")
        result: Dict[str, Any] = Field(..., description="Wynik wykonania przepływu")
        execution_time: float = Field(..., description="Czas wykonania przepływu (w sekundach)")
        timestamp: str = Field(..., description="Czas zakończenia przepływu")
    
    class FlowDefinition(BaseModel):
        """Model definicji przepływu."""
        flow_id: str = Field(..., description="Identyfikator przepływu")
        name: str = Field(..., description="Nazwa przepływu")
        description: Optional[str] = Field(None, description="Opis przepływu")
        tasks: List[str] = Field(..., description="Lista zadań w przepływie")
        connections: List[List[str]] = Field(..., description="Lista połączeń między zadaniami")
    
    class APIConfig(BaseModel):
        """Model konfiguracji API."""
        host: str = Field("0.0.0.0", description="Host API")
        port: int = Field(8000, description="Port API")
        debug: bool = Field(False, description="Tryb debugowania")
        allowed_origins: List[str] = Field(["*"], description="Dozwolone źródła CORS")
        api_prefix: str = Field("/api/v1", description="Prefiks API")
        require_auth: bool = Field(False, description="Czy wymagać uwierzytelniania")
        auth_token: str = Field("", description="Token uwierzytelniania")
        exposed_flows: List[str] = Field([], description="Lista udostępnionych przepływów")


def load_api_config() -> Dict[str, Any]:
    """
    Ładuje konfigurację API.
    
    Returns:
        Konfiguracja API
    """
    if not os.path.exists(API_CONFIG_FILE):
        # Tworzenie domyślnej konfiguracji
        with open(API_CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_API_CONFIG, f, indent=4)
        return DEFAULT_API_CONFIG
    
    try:
        with open(API_CONFIG_FILE, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Błąd ładowania konfiguracji API: {str(e)}")
        return DEFAULT_API_CONFIG


def save_api_config(config: Dict[str, Any]):
    """
    Zapisuje konfigurację API.
    
    Args:
        config: Konfiguracja API
    """
    try:
        with open(API_CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logger.error(f"Błąd zapisywania konfiguracji API: {str(e)}")


def expose_flow(flow_id: str) -> bool:
    """
    Udostępnia przepływ jako endpoint API.
    
    Args:
        flow_id: Identyfikator przepływu lub ścieżka do pliku DSL
        
    Returns:
        True, jeśli udostępniono pomyślnie
    """
    config = load_api_config()
    
    # Sprawdzenie, czy przepływ istnieje
    if os.path.isabs(flow_id) and os.path.exists(flow_id):
        flow_path = flow_id
    else:
        flow_path = DSL_DIR / f"{flow_id}.taskinity"
        if not os.path.exists(flow_path):
            logger.error(f"Nie znaleziono przepływu: {flow_id}")
            return False
    
    # Dodanie przepływu do listy udostępnionych
    if flow_id not in config["exposed_flows"]:
        config["exposed_flows"].append(flow_id)
        save_api_config(config)
        logger.info(f"Udostępniono przepływ: {flow_id}")
    
    return True


def unexpose_flow(flow_id: str) -> bool:
    """
    Usuwa udostępnienie przepływu.
    
    Args:
        flow_id: Identyfikator przepływu
        
    Returns:
        True, jeśli usunięto pomyślnie
    """
    config = load_api_config()
    
    if flow_id in config["exposed_flows"]:
        config["exposed_flows"].remove(flow_id)
        save_api_config(config)
        logger.info(f"Usunięto udostępnienie przepływu: {flow_id}")
        return True
    
    return False


def list_exposed_flows() -> List[str]:
    """
    Zwraca listę udostępnionych przepływów.
    
    Returns:
        Lista identyfikatorów przepływów
    """
    config = load_api_config()
    return config["exposed_flows"]


@timed_execution
def execute_flow_api(flow_id: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Wykonuje przepływ przez API.
    
    Args:
        flow_id: Identyfikator przepływu
        input_data: Dane wejściowe dla przepływu
        
    Returns:
        Wynik wykonania przepływu
    """
    start_time = datetime.now()
    
    try:
        # Ładowanie DSL
        if os.path.isabs(flow_id) and os.path.exists(flow_id):
            dsl_file = flow_id
        else:
            dsl_file = DSL_DIR / f"{flow_id}.taskinity"
            if not os.path.exists(dsl_file):
                raise FileNotFoundError(f"Nie znaleziono przepływu: {flow_id}")
        
        dsl_content = load_dsl(str(dsl_file))
        
        # Wykonanie przepływu
        result = run_flow_from_dsl(dsl_content, input_data or {})
        
        # Obliczenie czasu wykonania
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            "flow_id": flow_id,
            "status": "SUCCESS",
            "result": result,
            "execution_time": execution_time,
            "timestamp": end_time.isoformat()
        }
    
    except Exception as e:
        # Obliczenie czasu wykonania
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        logger.error(f"Błąd wykonania przepływu {flow_id}: {str(e)}")
        
        return {
            "flow_id": flow_id,
            "status": "ERROR",
            "result": {"error": str(e)},
            "execution_time": execution_time,
            "timestamp": end_time.isoformat()
        }


def get_flow_definition(flow_id: str) -> Dict[str, Any]:
    """
    Zwraca definicję przepływu.
    
    Args:
        flow_id: Identyfikator przepływu
        
    Returns:
        Definicja przepływu
    """
    try:
        # Ładowanie DSL
        if os.path.isabs(flow_id) and os.path.exists(flow_id):
            dsl_file = flow_id
        else:
            dsl_file = DSL_DIR / f"{flow_id}.taskinity"
            if not os.path.exists(dsl_file):
                raise FileNotFoundError(f"Nie znaleziono przepływu: {flow_id}")
        
        dsl_content = load_dsl(str(dsl_file))
        flow_def = parse_dsl(dsl_content)
        
        return {
            "flow_id": flow_id,
            "name": flow_def.get("name", ""),
            "description": flow_def.get("description", ""),
            "tasks": list(flow_def.get("tasks", {}).keys()),
            "connections": flow_def.get("connections", [])
        }
    
    except Exception as e:
        logger.error(f"Błąd pobierania definicji przepływu {flow_id}: {str(e)}")
        return {
            "flow_id": flow_id,
            "error": str(e)
        }


def create_api_app() -> Any:
    """
    Tworzy aplikację API.
    
    Returns:
        Aplikacja FastAPI lub None, jeśli FastAPI nie jest dostępne
    """
    if not FASTAPI_AVAILABLE:
        logger.error("FastAPI nie jest zainstalowane. Zainstaluj pakiet fastapi, aby korzystać z API.")
        return None
    
    config = load_api_config()
    
    # Tworzenie aplikacji FastAPI
    app = FastAPI(
        title="Taskinity API",
        description="API do zarządzania przepływami Taskinity",
        version="1.0.0"
    )
    
    # Konfiguracja CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config["allowed_origins"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Funkcja do weryfikacji tokenu
    async def verify_token(authorization: str = Query(None)):
        if not config["require_auth"]:
            return True
        
        if not authorization:
            raise HTTPException(status_code=401, detail="Brak tokenu uwierzytelniania")
        
        token = authorization.replace("Bearer ", "")
        if token != config["auth_token"]:
            raise HTTPException(status_code=401, detail="Nieprawidłowy token uwierzytelniania")
        
        return True
    
    # Endpoint do wykonania przepływu
    @app.post(f"{config['api_prefix']}/flows/{{flow_id}}/execute", response_model=FlowOutput)
    async def execute_flow(
        flow_id: str = PathParam(..., description="Identyfikator przepływu"),
        flow_input: FlowInput = Body(..., description="Dane wejściowe dla przepływu"),
        _: bool = Depends(verify_token)
    ):
        # Sprawdzenie, czy przepływ jest udostępniony
        if flow_id not in config["exposed_flows"]:
            raise HTTPException(status_code=404, detail=f"Przepływ {flow_id} nie jest udostępniony")
        
        # Wykonanie przepływu
        result = execute_flow_api(flow_id, flow_input.inputs)
        
        if result["status"] == "ERROR":
            return JSONResponse(
                status_code=500,
                content=result
            )
        
        return result
    
    # Endpoint do pobierania definicji przepływu
    @app.get(f"{config['api_prefix']}/flows/{{flow_id}}", response_model=FlowDefinition)
    async def get_flow(
        flow_id: str = PathParam(..., description="Identyfikator przepływu"),
        _: bool = Depends(verify_token)
    ):
        # Sprawdzenie, czy przepływ jest udostępniony
        if flow_id not in config["exposed_flows"]:
            raise HTTPException(status_code=404, detail=f"Przepływ {flow_id} nie jest udostępniony")
        
        # Pobieranie definicji przepływu
        flow_def = get_flow_definition(flow_id)
        
        if "error" in flow_def:
            raise HTTPException(status_code=500, detail=flow_def["error"])
        
        return flow_def
    
    # Endpoint do listowania udostępnionych przepływów
    @app.get(f"{config['api_prefix']}/flows", response_model=List[str])
    async def list_flows_endpoint(_: bool = Depends(verify_token)):
        return list_exposed_flows()
    
    return app


def run_api_server(host: Optional[str] = None, port: Optional[int] = None, debug: Optional[bool] = None):
    """
    Uruchamia serwer API.
    
    Args:
        host: Host serwera
        port: Port serwera
        debug: Tryb debugowania
    """
    if not FASTAPI_AVAILABLE:
        logger.error("FastAPI nie jest zainstalowane. Zainstaluj pakiet fastapi, aby korzystać z API.")
        return
    
    try:
        import uvicorn
    except ImportError:
        logger.error("Uvicorn nie jest zainstalowany. Zainstaluj pakiet uvicorn, aby uruchomić serwer API.")
        return
    
    config = load_api_config()
    
    # Ustawienie parametrów serwera
    server_host = host or config["host"]
    server_port = port or config["port"]
    server_debug = debug if debug is not None else config["debug"]
    
    # Tworzenie aplikacji
    app = create_api_app()
    
    if not app:
        return
    
    # Uruchomienie serwera
    logger.info(f"Uruchamianie serwera API na {server_host}:{server_port}")
    uvicorn.run(app, host=server_host, port=server_port)


class TaskinityAPI:
    """Klasa do zarządzania API Taskinity."""
    
    def __init__(self):
        """Inicjalizuje zarządcę API."""
        self.config = load_api_config()
    
    def expose_flow(self, flow_id: str) -> bool:
        """
        Udostępnia przepływ jako endpoint API.
        
        Args:
            flow_id: Identyfikator przepływu
            
        Returns:
            True, jeśli udostępniono pomyślnie
        """
        return expose_flow(flow_id)
    
    def unexpose_flow(self, flow_id: str) -> bool:
        """
        Usuwa udostępnienie przepływu.
        
        Args:
            flow_id: Identyfikator przepływu
            
        Returns:
            True, jeśli usunięto pomyślnie
        """
        return unexpose_flow(flow_id)
    
    def list_exposed_flows(self) -> List[str]:
        """
        Zwraca listę udostępnionych przepływów.
        
        Returns:
            Lista identyfikatorów przepływów
        """
        return list_exposed_flows()
    
    def configure(self, host: Optional[str] = None, port: Optional[int] = None,
                 debug: Optional[bool] = None, require_auth: Optional[bool] = None,
                 auth_token: Optional[str] = None, allowed_origins: Optional[List[str]] = None,
                 api_prefix: Optional[str] = None) -> Dict[str, Any]:
        """
        Konfiguruje API.
        
        Args:
            host: Host serwera
            port: Port serwera
            debug: Tryb debugowania
            require_auth: Czy wymagać uwierzytelniania
            auth_token: Token uwierzytelniania
            allowed_origins: Dozwolone źródła CORS
            api_prefix: Prefiks API
            
        Returns:
            Zaktualizowana konfiguracja
        """
        if host is not None:
            self.config["host"] = host
        
        if port is not None:
            self.config["port"] = port
        
        if debug is not None:
            self.config["debug"] = debug
        
        if require_auth is not None:
            self.config["require_auth"] = require_auth
        
        if auth_token is not None:
            self.config["auth_token"] = auth_token
        
        if allowed_origins is not None:
            self.config["allowed_origins"] = allowed_origins
        
        if api_prefix is not None:
            self.config["api_prefix"] = api_prefix
        
        save_api_config(self.config)
        return self.config
    
    def run_server(self, host: Optional[str] = None, port: Optional[int] = None, debug: Optional[bool] = None):
        """
        Uruchamia serwer API.
        
        Args:
            host: Host serwera
            port: Port serwera
            debug: Tryb debugowania
        """
        run_api_server(host, port, debug)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Użycie: python api.py [run|expose|unexpose|list|configure]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "run":
        host = sys.argv[2] if len(sys.argv) > 2 else None
        port = int(sys.argv[3]) if len(sys.argv) > 3 else None
        
        run_api_server(host, port)
    
    elif command == "expose" and len(sys.argv) >= 3:
        flow_id = sys.argv[2]
        
        if expose_flow(flow_id):
            print(f"Udostępniono przepływ: {flow_id}")
        else:
            print(f"Nie udało się udostępnić przepływu: {flow_id}")
    
    elif command == "unexpose" and len(sys.argv) >= 3:
        flow_id = sys.argv[2]
        
        if unexpose_flow(flow_id):
            print(f"Usunięto udostępnienie przepływu: {flow_id}")
        else:
            print(f"Nie znaleziono udostępnienia przepływu: {flow_id}")
    
    elif command == "list":
        flows = list_exposed_flows()
        
        print(f"Udostępnione przepływy ({len(flows)}):")
        for flow in flows:
            print(f"- {flow}")
    
    elif command == "configure":
        config = load_api_config()
        
        print("Aktualna konfiguracja:")
        print(json.dumps(config, indent=2))
        
        # Przykładowa konfiguracja
        if len(sys.argv) > 2 and sys.argv[2] == "interactive":
            host = input(f"Host [{config['host']}]: ") or config["host"]
            port = int(input(f"Port [{config['port']}]: ") or config["port"])
            debug = input(f"Debug [{config['debug']}]: ").lower() in ["true", "t", "1"] if input(f"Debug [{config['debug']}]: ") else config["debug"]
            require_auth = input(f"Wymagaj uwierzytelniania [{config['require_auth']}]: ").lower() in ["true", "t", "1"] if input(f"Wymagaj uwierzytelniania [{config['require_auth']}]: ") else config["require_auth"]
            
            if require_auth:
                auth_token = input(f"Token uwierzytelniania: ") or config["auth_token"]
            else:
                auth_token = ""
            
            api = TaskinityAPI()
            updated_config = api.configure(
                host=host,
                port=port,
                debug=debug,
                require_auth=require_auth,
                auth_token=auth_token
            )
            
            print("Zaktualizowana konfiguracja:")
            print(json.dumps(updated_config, indent=2))
    
    else:
        print("Nieznane polecenie")
        print("Użycie: python api.py [run|expose|unexpose|list|configure]")
