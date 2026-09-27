import os
import logging
from datetime import datetime, timezone

import psycopg2

from api_request import INDONESIA_CITIES, fetch_data

logger = logging.getLogger(__name__)


def connect_to_db():
    logger.info("Connecting to the PostgreSQL database...")
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
        logger.error("Error connecting to the database: %s", e)
        raise


def get_city_id(conn, city_name: str) -> int:
    """Look up city_id from raw.city dimension table."""
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT city_id FROM raw.city WHERE city_name = %s",
            (city_name,)
        )
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"City not found in raw.city: {city_name}")
        return row[0]


REQUIRED_API_KEYS = ('main', 'weather', 'wind', 'coord', 'dt', 'clouds')


def kelvin_to_celsius(k: float) -> float:
    return round(k - 273.15, 2)


def validate_weather_data(data: dict) -> None:
    """Validate API response structure and value ranges."""
    for key in REQUIRED_API_KEYS:
        if key not in data:
            raise ValueError(f'Missing required key: {key}')

    temp_celsius = data['main']['temp'] - 273.15
    if not (-50 <= temp_celsius <= 60):
        raise ValueError(f'Temperature out of range: {temp_celsius:.1f}C')

    humidity = data['main']['humidity']
    if not (0 <= humidity <= 100):
        raise ValueError(f'Humidity out of range: {humidity}%')

    if data['main']['pressure'] <= 0:
        raise ValueError(f'Invalid pressure: {data["main"]["pressure"]}')


def insert_records(conn, city_id: int, city_name: str, data: dict) -> None:
    """Insert a single weather observation into raw.weather_data."""
    logger.info("Inserting record for %s...", city_name)
    main = data['main']
    weather = data['weather'][0]
    wind = data['wind']

    observed_at = datetime.fromtimestamp(data['dt'], tz=timezone.utc)

    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO raw.weather_data(
                city_id,
                temperature_c, feels_like_c, temp_min_c, temp_max_c,
                humidity, pressure_hpa,
                weather_main, weather_desc,
                wind_speed_ms, wind_deg,
                cloud_pct, visibility_m,
                observed_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (city_id, observed_at) DO NOTHING
        """, (
            city_id,
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
    logger.info("Record for %s inserted successfully.", city_name)


def main() -> None:
    conn = None
    try:
        conn = connect_to_db()

        for city in INDONESIA_CITIES:
            city_id = get_city_id(conn, city["name"])
            data = fetch_data(city)
            validate_weather_data(data)
            insert_records(conn, city_id, city["name"], data)

    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    main()
