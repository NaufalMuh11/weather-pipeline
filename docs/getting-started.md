# Getting Started

## Prerequisites

- Docker Desktop (with Docker Compose v2)
- OpenWeatherMap API key (free tier works)

## Clone Repository

```bash
git clone https://github.com/your-username/weather-data-engineer.git
cd weather-data-engineer
```

## Configure Environment

```bash
cp .env.example .env
cp dbt/profiles.yml.example dbt/profiles.yml
```

Set your values in `.env`:

```text
POSTGRES_PASSWORD=your_secure_password
OPENWEATHER_API_KEY=your_api_key_here
```

## Start Services

```bash
docker compose up -d
```

## Access Services

| Service | URL |
|---------|-----|
| Airflow | http://localhost:8000 |
| Superset | http://localhost:8088 |
| PostgreSQL | localhost:5000 |

## Common Tasks

### View Airflow logs

```bash
docker logs airflow_container -f
```

### Run dbt manually

```bash
docker exec -it dbt_container dbt run
```

### Connect to PostgreSQL

```bash
docker exec -it postgres_container psql -U user_d -d weather_db
```

### Reset Superset

```bash
docker compose down -v
docker compose up -d
```

### Stop everything

```bash
docker compose down
```

## Troubleshooting

**Superset init fails with `bash\r` error**

This means a shell script has Windows line endings. The `.gitattributes` in this repo should prevent that. If it still happens:

```bash
sed -i 's/\r$//' docker/docker-init.sh docker/docker-bootstrap.sh
```

**dbt cannot find profile `my_project`**

Make sure you copied the profiles file:

```bash
cp dbt/profiles.yml.example dbt/profiles.yml
```

**Airflow dbt task fails with connection error**

The dbt container needs to reach PostgreSQL via the Docker network. Check that `DOCKER_NETWORK` in `.env` matches your setup. The default is `weather-data-engineer_my-network`.

**Port already in use**

Change the host port in `.env` or `docker-compose.yaml`. For example, to move PostgreSQL to port 5433:

```yaml
ports:
  - "5433:5432"
```

**OpenWeatherMap API returns 401**

Verify your API key is correct in `.env`. Free tier keys may take up to 2 hours to activate after registration.
