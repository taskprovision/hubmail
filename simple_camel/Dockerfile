FROM python:3.9-slim

WORKDIR /app

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Kopiowanie plików projektu
COPY requirements.txt .
COPY .env.example .

# Instalacja zależności Pythona
RUN pip install --no-cache-dir -r requirements.txt

# Tworzenie katalogów
RUN mkdir -p attachments logs static templates

# Kopiowanie kodu źródłowego
COPY *.py .
COPY config.yaml .

# Ustawienie zmiennych środowiskowych
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Otworzenie portu dla dashboardu
EXPOSE 8000

# Uruchomienie aplikacji
CMD ["python", "start.py"]
