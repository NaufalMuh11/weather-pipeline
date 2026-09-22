import requests, os

API_KEY = os.getenv("OPENWEATHER_API_KEY")

INDONESIA_CITIES = [
    {"name": "Jakarta", "lat": -6.1750, "lon": 106.8650},
    {"name": "Bandung", "lat": -6.9175, "lon": 107.6191},
    {"name": "Yogyakarta", "lat": -7.7956, "lon": 110.3695},
]


def build_url(lat, lon):
    return f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"


def fetch_data(city):
    print(f"Fetching weather data for {city['name']}...")
    try:
        response = requests.get(build_url(city["lat"], city["lon"]))
        response.raise_for_status()
        print(f"API response received for {city['name']}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching {city['name']}: {e}")
        raise


def fetch_all_cities():
    results = []
    for city in INDONESIA_CITIES:
        data = fetch_data(city)
        results.append(data)
    return results


if __name__ == "__main__":
    all_data = fetch_all_cities()
    print(f"Fetched {len(all_data)} city records")