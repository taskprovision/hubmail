#!/usr/bin/env python3
"""
Przykład integracji z API pogodowym z wykorzystaniem Taskinity.
"""
import os
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Import funkcji z Taskinity
from taskinity import task, flow, run_flow_from_dsl, save_dsl, retry, timed_execution

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

# Konfiguracja API
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "demo_key")
WEATHER_API_URL = os.environ.get("WEATHER_API_URL", "https://api.openweathermap.org/data/2.5/weather")
MOCK_API = os.environ.get("USE_MOCK_API", "true").lower() == "true"

# Jeśli używamy mockowego API, używamy lokalnego serwera
if MOCK_API:
    WEATHER_API_URL = os.environ.get("MOCK_API_URL", "http://localhost:3000/api/weather")


# Definicja zadań
@task(name="PrepareWeatherRequest", description="Przygotowuje parametry zapytania do API pogodowego")
def prepare_weather_request(city=None, country_code=None, lat=None, lon=None):
    """Przygotowuje parametry zapytania do API pogodowego."""
    print("Przygotowywanie parametrów zapytania do API pogodowego...")
    
    params = {
        "appid": WEATHER_API_KEY,
        "units": "metric"  # Używamy jednostek metrycznych (Celsjusz)
    }
    
    # Określenie lokalizacji
    if city:
        if country_code:
            params["q"] = f"{city},{country_code}"
        else:
            params["q"] = city
        print(f"Przygotowano zapytanie dla miasta: {city}")
    elif lat is not None and lon is not None:
        params["lat"] = lat
        params["lon"] = lon
        print(f"Przygotowano zapytanie dla współrzędnych: {lat}, {lon}")
    else:
        # Domyślnie: Warszawa, Polska
        params["q"] = "Warsaw,PL"
        print("Używam domyślnej lokalizacji: Warszawa, Polska")
    
    return {
        "api_url": WEATHER_API_URL,
        "params": params
    }


@task(name="MakeWeatherRequest", description="Wykonuje zapytanie do API pogodowego")
@retry(max_attempts=3, delay=2.0, backoff=2.0, exceptions=(requests.RequestException,))
@timed_execution
def make_weather_request(inputs):
    """Wykonuje zapytanie do API pogodowego."""
    api_url = inputs["PrepareWeatherRequest"]["api_url"]
    params = inputs["PrepareWeatherRequest"]["params"]
    
    print(f"Wykonywanie zapytania do API: {api_url}")
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()  # Rzuca wyjątek dla kodów błędów HTTP
        
        data = response.json()
        print(f"Otrzymano odpowiedź z API: {response.status_code}")
        
        return {
            "status": "success",
            "data": data,
            "http_status": response.status_code
        }
    except requests.RequestException as e:
        print(f"Błąd zapytania do API: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "http_status": getattr(e.response, "status_code", None) if hasattr(e, "response") else None
        }


@task(name="ProcessWeatherData", description="Przetwarza dane pogodowe")
def process_weather_data(inputs):
    """Przetwarza dane pogodowe."""
    response = inputs["MakeWeatherRequest"]
    
    if response["status"] == "error":
        print(f"Nie można przetworzyć danych: {response['error']}")
        return {
            "status": "error",
            "error": response["error"]
        }
    
    data = response["data"]
    
    # Przetwarzanie danych
    print("Przetwarzanie danych pogodowych...")
    
    try:
        city_name = data.get("name", "Nieznane")
        country = data.get("sys", {}).get("country", "")
        
        # Dane pogodowe
        weather_main = data.get("weather", [{}])[0].get("main", "")
        weather_description = data.get("weather", [{}])[0].get("description", "")
        
        # Temperatura
        temp = data.get("main", {}).get("temp")
        feels_like = data.get("main", {}).get("feels_like")
        temp_min = data.get("main", {}).get("temp_min")
        temp_max = data.get("main", {}).get("temp_max")
        
        # Inne dane
        humidity = data.get("main", {}).get("humidity")
        pressure = data.get("main", {}).get("pressure")
        wind_speed = data.get("wind", {}).get("speed")
        wind_direction = data.get("wind", {}).get("deg")
        
        # Czas pomiaru
        timestamp = data.get("dt", 0)
        measurement_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        # Tworzenie przetworzonego obiektu
        processed_data = {
            "location": {
                "city": city_name,
                "country": country
            },
            "weather": {
                "main": weather_main,
                "description": weather_description
            },
            "temperature": {
                "current": temp,
                "feels_like": feels_like,
                "min": temp_min,
                "max": temp_max
            },
            "conditions": {
                "humidity": humidity,
                "pressure": pressure,
                "wind_speed": wind_speed,
                "wind_direction": wind_direction
            },
            "measurement_time": measurement_time
        }
        
        print(f"Przetworzono dane pogodowe dla: {city_name}, {country}")
        return {
            "status": "success",
            "processed_data": processed_data
        }
    
    except Exception as e:
        print(f"Błąd przetwarzania danych: {str(e)}")
        return {
            "status": "error",
            "error": f"Błąd przetwarzania danych: {str(e)}"
        }


@task(name="GenerateWeatherReport", description="Generuje raport pogodowy")
def generate_weather_report(inputs):
    """Generuje raport pogodowy."""
    response = inputs["ProcessWeatherData"]
    
    if response["status"] == "error":
        print(f"Nie można wygenerować raportu: {response['error']}")
        return {
            "status": "error",
            "error": response["error"]
        }
    
    data = response["processed_data"]
    
    # Generowanie raportu
    print("Generowanie raportu pogodowego...")
    
    # Raport tekstowy
    report_text = f"""
=== RAPORT POGODOWY ===

Lokalizacja: {data['location']['city']}, {data['location']['country']}
Czas pomiaru: {data['measurement_time']}

Pogoda: {data['weather']['main']} ({data['weather']['description']})

Temperatura:
- Aktualna: {data['temperature']['current']}°C
- Odczuwalna: {data['temperature']['feels_like']}°C
- Minimalna: {data['temperature']['min']}°C
- Maksymalna: {data['temperature']['max']}°C

Warunki:
- Wilgotność: {data['conditions']['humidity']}%
- Ciśnienie: {data['conditions']['pressure']} hPa
- Wiatr: {data['conditions']['wind_speed']} m/s, kierunek: {data['conditions']['wind_direction']}°

Raport wygenerowany przez Taskinity
"""
    
    # Zapisanie raportu
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = OUTPUT_DIR / f"weather_report_{timestamp}.txt"
    json_file = OUTPUT_DIR / f"weather_data_{timestamp}.json"
    
    with open(report_file, "w") as f:
        f.write(report_text)
    
    with open(json_file, "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"Zapisano raport do: {report_file}")
    print(f"Zapisano dane JSON do: {json_file}")
    
    return {
        "status": "success",
        "report_file": str(report_file),
        "json_file": str(json_file),
        "report_text": report_text,
        "data": data
    }


# Definicja przepływu
@flow(name="WeatherAPIFlow", description="Przepływ integracji z API pogodowym")
def weather_api_flow(city=None, country_code=None, lat=None, lon=None):
    # Definicja zadań
    prepare = prepare_weather_request(city, country_code, lat, lon)
    make_request = make_weather_request({"PrepareWeatherRequest": prepare})
    process = process_weather_data({"MakeWeatherRequest": make_request})
    report = generate_weather_report({"ProcessWeatherData": process})
    
    # Definicja przepływu
    return {
        "tasks": {
            "PrepareWeatherRequest": prepare,
            "MakeWeatherRequest": make_request,
            "ProcessWeatherData": process,
            "GenerateWeatherReport": report
        },
        "connections": [
            ("PrepareWeatherRequest", "MakeWeatherRequest"),
            ("MakeWeatherRequest", "ProcessWeatherData"),
            ("ProcessWeatherData", "GenerateWeatherReport")
        ]
    }


# Definicja przepływu w DSL
WEATHER_API_DSL = """
flow WeatherAPIFlow:
    description: "Przepływ integracji z API pogodowym"
    
    task PrepareWeatherRequest:
        description: "Przygotowuje parametry zapytania do API pogodowego"
        code: |
            import os
            from dotenv import load_dotenv
            
            # Ładowanie zmiennych środowiskowych
            load_dotenv()
            
            # Konfiguracja API
            WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "demo_key")
            WEATHER_API_URL = os.environ.get("WEATHER_API_URL", "https://api.openweathermap.org/data/2.5/weather")
            MOCK_API = os.environ.get("USE_MOCK_API", "true").lower() == "true"
            
            # Jeśli używamy mockowego API, używamy lokalnego serwera
            if MOCK_API:
                WEATHER_API_URL = os.environ.get("MOCK_API_URL", "http://localhost:3000/api/weather")
            
            print("Przygotowywanie parametrów zapytania do API pogodowego...")
            
            # Parametry z wejścia
            city = inputs.get("city")
            country_code = inputs.get("country_code")
            lat = inputs.get("lat")
            lon = inputs.get("lon")
            
            params = {
                "appid": WEATHER_API_KEY,
                "units": "metric"  # Używamy jednostek metrycznych (Celsjusz)
            }
            
            # Określenie lokalizacji
            if city:
                if country_code:
                    params["q"] = f"{city},{country_code}"
                else:
                    params["q"] = city
                print(f"Przygotowano zapytanie dla miasta: {city}")
            elif lat is not None and lon is not None:
                params["lat"] = lat
                params["lon"] = lon
                print(f"Przygotowano zapytanie dla współrzędnych: {lat}, {lon}")
            else:
                # Domyślnie: Warszawa, Polska
                params["q"] = "Warsaw,PL"
                print("Używam domyślnej lokalizacji: Warszawa, Polska")
            
            return {
                "api_url": WEATHER_API_URL,
                "params": params
            }
    
    task MakeWeatherRequest:
        description: "Wykonuje zapytanie do API pogodowego"
        code: |
            import requests
            import time
            
            api_url = inputs["PrepareWeatherRequest"]["api_url"]
            params = inputs["PrepareWeatherRequest"]["params"]
            
            print(f"Wykonywanie zapytania do API: {api_url}")
            
            # Funkcja z mechanizmem ponawiania
            def make_request_with_retry(url, params, max_attempts=3, delay=2.0, backoff=2.0):
                current_delay = delay
                
                for attempt in range(1, max_attempts + 1):
                    try:
                        response = requests.get(url, params=params, timeout=10)
                        response.raise_for_status()  # Rzuca wyjątek dla kodów błędów HTTP
                        
                        return {
                            "status": "success",
                            "data": response.json(),
                            "http_status": response.status_code
                        }
                    except requests.RequestException as e:
                        print(f"Próba {attempt}/{max_attempts}: Błąd zapytania do API: {str(e)}")
                        
                        if attempt < max_attempts:
                            print(f"Ponowienie za {current_delay:.2f} s")
                            time.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            return {
                                "status": "error",
                                "error": str(e),
                                "http_status": getattr(e.response, "status_code", None) if hasattr(e, "response") else None
                            }
            
            return make_request_with_retry(api_url, params)
    
    task ProcessWeatherData:
        description: "Przetwarza dane pogodowe"
        code: |
            from datetime import datetime
            
            response = inputs["MakeWeatherRequest"]
            
            if response["status"] == "error":
                print(f"Nie można przetworzyć danych: {response['error']}")
                return {
                    "status": "error",
                    "error": response["error"]
                }
            
            data = response["data"]
            
            # Przetwarzanie danych
            print("Przetwarzanie danych pogodowych...")
            
            try:
                city_name = data.get("name", "Nieznane")
                country = data.get("sys", {}).get("country", "")
                
                # Dane pogodowe
                weather_main = data.get("weather", [{}])[0].get("main", "")
                weather_description = data.get("weather", [{}])[0].get("description", "")
                
                # Temperatura
                temp = data.get("main", {}).get("temp")
                feels_like = data.get("main", {}).get("feels_like")
                temp_min = data.get("main", {}).get("temp_min")
                temp_max = data.get("main", {}).get("temp_max")
                
                # Inne dane
                humidity = data.get("main", {}).get("humidity")
                pressure = data.get("main", {}).get("pressure")
                wind_speed = data.get("wind", {}).get("speed")
                wind_direction = data.get("wind", {}).get("deg")
                
                # Czas pomiaru
                timestamp = data.get("dt", 0)
                measurement_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                
                # Tworzenie przetworzonego obiektu
                processed_data = {
                    "location": {
                        "city": city_name,
                        "country": country
                    },
                    "weather": {
                        "main": weather_main,
                        "description": weather_description
                    },
                    "temperature": {
                        "current": temp,
                        "feels_like": feels_like,
                        "min": temp_min,
                        "max": temp_max
                    },
                    "conditions": {
                        "humidity": humidity,
                        "pressure": pressure,
                        "wind_speed": wind_speed,
                        "wind_direction": wind_direction
                    },
                    "measurement_time": measurement_time
                }
                
                print(f"Przetworzono dane pogodowe dla: {city_name}, {country}")
                return {
                    "status": "success",
                    "processed_data": processed_data
                }
            
            except Exception as e:
                print(f"Błąd przetwarzania danych: {str(e)}")
                return {
                    "status": "error",
                    "error": f"Błąd przetwarzania danych: {str(e)}"
                }
    
    task GenerateWeatherReport:
        description: "Generuje raport pogodowy"
        code: |
            import os
            import json
            from datetime import datetime
            from pathlib import Path
            
            response = inputs["ProcessWeatherData"]
            
            if response["status"] == "error":
                print(f"Nie można wygenerować raportu: {response['error']}")
                return {
                    "status": "error",
                    "error": response["error"]
                }
            
            data = response["processed_data"]
            
            # Generowanie raportu
            print("Generowanie raportu pogodowego...")
            
            # Raport tekstowy
            report_text = f"""
=== RAPORT POGODOWY ===

Lokalizacja: {data['location']['city']}, {data['location']['country']}
Czas pomiaru: {data['measurement_time']}

Pogoda: {data['weather']['main']} ({data['weather']['description']})

Temperatura:
- Aktualna: {data['temperature']['current']}°C
- Odczuwalna: {data['temperature']['feels_like']}°C
- Minimalna: {data['temperature']['min']}°C
- Maksymalna: {data['temperature']['max']}°C

Warunki:
- Wilgotność: {data['conditions']['humidity']}%
- Ciśnienie: {data['conditions']['pressure']} hPa
- Wiatr: {data['conditions']['wind_speed']} m/s, kierunek: {data['conditions']['wind_direction']}°

Raport wygenerowany przez Taskinity
"""
            
            # Zapisanie raportu
            OUTPUT_DIR = Path("output")
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = OUTPUT_DIR / f"weather_report_{timestamp}.txt"
            json_file = OUTPUT_DIR / f"weather_data_{timestamp}.json"
            
            with open(report_file, "w") as f:
                f.write(report_text)
            
            with open(json_file, "w") as f:
                json.dump(data, f, indent=4)
            
            print(f"Zapisano raport do: {report_file}")
            print(f"Zapisano dane JSON do: {json_file}")
            
            return {
                "status": "success",
                "report_file": str(report_file),
                "json_file": str(json_file),
                "report_text": report_text,
                "data": data
            }
    
    PrepareWeatherRequest -> MakeWeatherRequest -> ProcessWeatherData -> GenerateWeatherReport
"""

# Zapisanie definicji DSL
def save_dsl_definition():
    """Zapisuje definicję DSL do pliku."""
    dsl_file = DSL_DIR / "weather_api.taskinity"
    with open(dsl_file, "w") as f:
        f.write(WEATHER_API_DSL)
    print(f"Zapisano definicję DSL do: {dsl_file}")
    return str(dsl_file)


if __name__ == "__main__":
    # Zapisanie definicji DSL
    dsl_file = save_dsl_definition()
    
    # Pobieranie parametrów z wiersza poleceń
    import sys
    
    if len(sys.argv) > 1:
        city = sys.argv[1]
        country_code = sys.argv[2] if len(sys.argv) > 2 else None
        
        print(f"Pobieranie danych pogodowych dla: {city}{', ' + country_code if country_code else ''}")
        
        # Uruchomienie przepływu z definicji DSL
        result = run_flow_from_dsl(
            WEATHER_API_DSL,
            {"city": city, "country_code": country_code}
        )
    else:
        print("Pobieranie danych pogodowych dla domyślnej lokalizacji")
        
        # Uruchomienie przepływu z definicji DSL
        result = run_flow_from_dsl(WEATHER_API_DSL, {})
    
    # Wyświetlenie wyniku
    if result["GenerateWeatherReport"]["status"] == "success":
        print("\nRaport pogodowy:")
        print(result["GenerateWeatherReport"]["report_text"])
    else:
        print("\nBłąd generowania raportu:")
        print(result["GenerateWeatherReport"]["error"])
    
    print("\nZakończono integrację z API pogodowym.")
