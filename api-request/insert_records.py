import os
import psycopg2
from datetime import datetime, timezone
from api_request import INDONESIA_CITIES, fetch_data


def connect_to_db():
    print("Connecting to the PostgreSQL database...")
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "database"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "weather_db"),
            user=os.getenv("DB_USER", "user_d"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        raise


def create_table(conn):
    print("Creating table if not exists...")
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE SCHEMA IF NOT EXISTS dev;
                CREATE TABLE IF NOT EXISTS dev.raw_weather_data (
                    id SERIAL PRIMARY KEY,
                    city TEXT,
                    lat FLOAT,
                    lon FLOAT,
                    temperature FLOAT,
                    feels_like FLOAT,
                    temp_min FLOAT,
                    temp_max FLOAT,
                    humidity INT,
                    pressure INT,
                    weather_main TEXT,
                    weather_description TEXT,
                    wind_speed FLOAT,
                    wind_deg INT,
                    clouds INT,
                    visibility INT,
                    observed_at TIMESTAMPTZ,
                    inserted_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
        conn.commit()
        print("Table created successfully.")
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")
        raise


def kelvin_to_celsius(k):
    return round(k - 273.15, 2)


def insert_records(conn, city_name: str, data: dict) -> None:
    print(f"Inserting record for {city_name}...")
    try:
        main = data['main']
        weather = data['weather'][0]
        wind = data['wind']
        coord = data['coord']

        observed_at = datetime.fromtimestamp(data['dt'], tz=timezone.utc)

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO dev.raw_weather_data(
                    city, lat, lon,
                    temperature, feels_like, temp_min, temp_max,
                    humidity, pressure,
                    weather_main, weather_description,
                    wind_speed, wind_deg,
                    clouds, visibility,
                    observed_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                city_name,
                coord['lat'],
                coord['lon'],
                kelvin_to_celsius(main['temp']),
                kelvin_to_celsius(main['feels_like']),
                kelvin_to_celsius(main['temp_min']),
                kelvin_to_celsius(main['temp_max']),
                main['humidity'],
                main['pressure'],
                weather['main'],
                weather['description'],
                wind['speed'],
                wind.get('deg'),
                data['clouds']['all'],
                data.get('visibility'),
                observed_at,
            ))
        conn.commit()
        print(f"Record for {city_name} inserted successfully.")
    except psycopg2.Error as e:
        print(f"Error inserting records: {e}")
        raise


def main():
    conn = None
    try:
        conn = connect_to_db()
        create_table(conn)

        for city in INDONESIA_CITIES:
            data = fetch_data(city)
            insert_records(conn, city["name"], data)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()