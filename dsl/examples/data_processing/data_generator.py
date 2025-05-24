#!/usr/bin/env python3
"""
Generator danych testowych dla przykładu przetwarzania danych.
Generuje dane CSV oraz wstawia je do bazy danych PostgreSQL.
"""
import os
import time
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from faker import Faker

# Inicjalizacja Faker
fake = Faker()

# Konfiguracja z zmiennych środowiskowych
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'taskinity')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'taskinity')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'taskinity_data')

GENERATE_ROWS = int(os.environ.get('GENERATE_ROWS', '1000'))
GENERATE_TABLES = os.environ.get('GENERATE_TABLES', 'sales,customers,products').split(',')

# Ścieżka do katalogu z danymi
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Połączenie do bazy danych
def get_db_engine():
    """Tworzy połączenie do bazy danych."""
    connection_string = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    return create_engine(connection_string)

# Generowanie danych sprzedażowych
def generate_sales_data(num_rows=1000):
    """Generuje dane sprzedażowe."""
    print(f"Generowanie {num_rows} wierszy danych sprzedażowych...")
    
    # Generowanie dat
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2023, 12, 31)
    days_between = (end_date - start_date).days
    
    # Generowanie danych
    data = {
        'sale_id': range(1, num_rows + 1),
        'date': [start_date + timedelta(days=random.randint(0, days_between)) for _ in range(num_rows)],
        'product_id': [random.randint(1, 100) for _ in range(num_rows)],
        'customer_id': [random.randint(1, 500) for _ in range(num_rows)],
        'quantity': [random.randint(1, 10) for _ in range(num_rows)],
        'unit_price': [round(random.uniform(10.0, 1000.0), 2) for _ in range(num_rows)],
        'discount': [round(random.uniform(0.0, 0.3), 2) for _ in range(num_rows)],
        'region': [random.choice(['North', 'South', 'East', 'West', 'Central']) for _ in range(num_rows)],
        'payment_method': [random.choice(['Credit Card', 'Cash', 'Bank Transfer', 'PayPal']) for _ in range(num_rows)]
    }
    
    # Obliczenie całkowitej wartości
    data['total_value'] = [
        round(data['quantity'][i] * data['unit_price'][i] * (1 - data['discount'][i]), 2)
        for i in range(num_rows)
    ]
    
    # Tworzenie DataFrame
    df = pd.DataFrame(data)
    
    # Zapisanie do CSV
    csv_file = os.path.join(DATA_DIR, 'sales_data.csv')
    df.to_csv(csv_file, index=False)
    print(f"Zapisano dane sprzedażowe do: {csv_file}")
    
    return df

# Generowanie danych klientów
def generate_customer_data(num_rows=500):
    """Generuje dane klientów."""
    print(f"Generowanie {num_rows} wierszy danych klientów...")
    
    # Generowanie danych
    data = {
        'customer_id': range(1, num_rows + 1),
        'name': [fake.name() for _ in range(num_rows)],
        'email': [fake.email() for _ in range(num_rows)],
        'phone': [fake.phone_number() for _ in range(num_rows)],
        'address': [fake.address().replace('\n', ', ') for _ in range(num_rows)],
        'city': [fake.city() for _ in range(num_rows)],
        'country': [fake.country() for _ in range(num_rows)],
        'registration_date': [fake.date_between(start_date='-3y', end_date='today') for _ in range(num_rows)],
        'customer_type': [random.choice(['Individual', 'Business', 'Government']) for _ in range(num_rows)],
        'loyalty_points': [random.randint(0, 10000) for _ in range(num_rows)]
    }
    
    # Tworzenie DataFrame
    df = pd.DataFrame(data)
    
    # Zapisanie do CSV
    csv_file = os.path.join(DATA_DIR, 'customers_data.csv')
    df.to_csv(csv_file, index=False)
    print(f"Zapisano dane klientów do: {csv_file}")
    
    return df

# Generowanie danych produktów
def generate_product_data(num_rows=100):
    """Generuje dane produktów."""
    print(f"Generowanie {num_rows} wierszy danych produktów...")
    
    # Kategorie produktów
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports', 'Toys', 'Food', 'Health & Beauty']
    
    # Generowanie danych
    data = {
        'product_id': range(1, num_rows + 1),
        'name': [f"{fake.word().capitalize()} {fake.word().capitalize()}" for _ in range(num_rows)],
        'description': [fake.text(max_nb_chars=200) for _ in range(num_rows)],
        'category': [random.choice(categories) for _ in range(num_rows)],
        'price': [round(random.uniform(10.0, 1000.0), 2) for _ in range(num_rows)],
        'stock_quantity': [random.randint(0, 1000) for _ in range(num_rows)],
        'supplier_id': [random.randint(1, 20) for _ in range(num_rows)],
        'rating': [round(random.uniform(1.0, 5.0), 1) for _ in range(num_rows)],
        'is_active': [random.choice([True, True, True, False]) for _ in range(num_rows)]  # 75% aktywnych
    }
    
    # Tworzenie DataFrame
    df = pd.DataFrame(data)
    
    # Zapisanie do CSV
    csv_file = os.path.join(DATA_DIR, 'products_data.csv')
    df.to_csv(csv_file, index=False)
    print(f"Zapisano dane produktów do: {csv_file}")
    
    return df

# Tworzenie tabel w bazie danych
def create_database_tables(engine):
    """Tworzy tabele w bazie danych."""
    Base = declarative_base()
    
    # Definicja tabeli sprzedaży
    class Sales(Base):
        __tablename__ = 'sales'
        
        sale_id = Column(Integer, primary_key=True)
        date = Column(Date)
        product_id = Column(Integer)
        customer_id = Column(Integer)
        quantity = Column(Integer)
        unit_price = Column(Float)
        discount = Column(Float)
        total_value = Column(Float)
        region = Column(String(50))
        payment_method = Column(String(50))
    
    # Definicja tabeli klientów
    class Customers(Base):
        __tablename__ = 'customers'
        
        customer_id = Column(Integer, primary_key=True)
        name = Column(String(100))
        email = Column(String(100))
        phone = Column(String(50))
        address = Column(Text)
        city = Column(String(100))
        country = Column(String(100))
        registration_date = Column(Date)
        customer_type = Column(String(50))
        loyalty_points = Column(Integer)
    
    # Definicja tabeli produktów
    class Products(Base):
        __tablename__ = 'products'
        
        product_id = Column(Integer, primary_key=True)
        name = Column(String(100))
        description = Column(Text)
        category = Column(String(50))
        price = Column(Float)
        stock_quantity = Column(Integer)
        supplier_id = Column(Integer)
        rating = Column(Float)
        is_active = Column(Integer)  # 1 = True, 0 = False
    
    # Tworzenie tabel
    Base.metadata.create_all(engine)
    print("Utworzono tabele w bazie danych")

# Wstawianie danych do bazy
def insert_data_to_db(engine, table_name, df):
    """Wstawia dane do bazy danych."""
    print(f"Wstawianie danych do tabeli {table_name}...")
    
    # Konwersja wartości logicznych na liczby dla SQLite
    if table_name == 'products' and 'is_active' in df.columns:
        df['is_active'] = df['is_active'].astype(int)
    
    # Wstawianie danych
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Wstawiono {len(df)} wierszy do tabeli {table_name}")

def main():
    """Główna funkcja generatora danych."""
    print("Rozpoczęcie generowania danych testowych...")
    
    # Oczekiwanie na dostępność bazy danych
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            engine = get_db_engine()
            engine.connect()
            print("Połączono z bazą danych")
            break
        except Exception as e:
            print(f"Próba {attempt+1}/{max_retries}: Nie można połączyć z bazą danych: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Ponowna próba za {retry_delay} sekund...")
                time.sleep(retry_delay)
            else:
                print("Nie udało się połączyć z bazą danych. Generowanie tylko plików CSV.")
                engine = None
    
    # Generowanie danych
    sales_df = None
    customers_df = None
    products_df = None
    
    if 'sales' in GENERATE_TABLES:
        sales_df = generate_sales_data(GENERATE_ROWS)
    
    if 'customers' in GENERATE_TABLES:
        customers_df = generate_customer_data(GENERATE_ROWS // 2)
    
    if 'products' in GENERATE_TABLES:
        products_df = generate_product_data(GENERATE_ROWS // 10)
    
    # Wstawianie danych do bazy danych
    if engine:
        try:
            create_database_tables(engine)
            
            if sales_df is not None:
                insert_data_to_db(engine, 'sales', sales_df)
            
            if customers_df is not None:
                insert_data_to_db(engine, 'customers', customers_df)
            
            if products_df is not None:
                insert_data_to_db(engine, 'products', products_df)
            
            print("Zakończono wstawianie danych do bazy danych")
        except Exception as e:
            print(f"Błąd podczas wstawiania danych do bazy danych: {str(e)}")
    
    print("Zakończono generowanie danych testowych")

if __name__ == "__main__":
    main()
