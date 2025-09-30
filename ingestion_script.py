# ingestion_script.py
#MT_Sku_Challenge

import os
import requests
import psycopg2
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv() # Load environment variables from .env file

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

API_URL = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD"
TABLE_NAME = "raw_gdp_data"

# --- EXTRACTION ---
def fetch_gdp_data():
    """
    Fetches all historical GDP data from the World Bank API, handling pagination.
    """
    all_data = []
    page = 1
    total_pages = 1 # We'll update this after the first API call

    print("Starting data ingestion from World Bank API...")

    while page <= total_pages:
        params = {
            'format': 'json',
            'page': page,
            'per_page': 1000 # Fetch more data per request to be efficient
        }
        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            metadata = data[0]
            total_pages = metadata['pages']
            
            records = data[1]
            if records:
                all_data.extend(records)

            print(f"Successfully fetched page {page}/{total_pages}.")
            page += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from API: {e}")
            return None
        except (KeyError, IndexError) as e:
            print(f"Error parsing API response format: {e}")
            return None

    print(f"Total records fetched: {len(all_data)}")
    return all_data

# --- LOADING ---
def load_data_to_postgres(data):
    """
    Loads the fetched data into a PostgreSQL table.
    The script is idempotent: it drops the table if it exists and recreates it.
    """
    if not data:
        print("No data to load.")
        return

    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        print("Successfully connected to PostgreSQL.")

        print(f"Dropping table '{TABLE_NAME}' if it exists...")
        cur.execute(f"DROP TABLE IF EXISTS {TABLE_NAME};")

        print(f"Creating table '{TABLE_NAME}'...")
        create_table_query = f"""
        CREATE TABLE {TABLE_NAME} (
            id SERIAL PRIMARY KEY,
            country_name TEXT,
            country_iso3_code VARCHAR(3),
            year INT,
            gdp_usd NUMERIC
        );
        """
        cur.execute(create_table_query)
        print("Table created successfully.")

        insert_data = [
            (
                record['country']['value'],
                record['countryiso3code'],
                int(record['date']),
                record['value']
            )
            for record in data
        ]

        print(f"Inserting {len(insert_data)} records into the database...")
        insert_query = f"""
        INSERT INTO {TABLE_NAME} (country_name, country_iso3_code, year, gdp_usd)
        VALUES (%s, %s, %s, %s);
        """
        cur.executemany(insert_query, insert_data)

        conn.commit()
        print("Data loaded successfully!")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            print("Database connection closed.")


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    gdp_data = fetch_gdp_data()
    if gdp_data:
        load_data_to_postgres(gdp_data)