-- ============================================================
-- Weather Data Warehouse Schema
-- Schemas: raw → staging → analytics
-- ============================================================

-- ----------------------------
-- SCHEMAS
-- ----------------------------
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

-- ----------------------------
-- RAW LAYER: City Dimension
-- ----------------------------
CREATE TABLE IF NOT EXISTS raw.city (
    city_id     SERIAL PRIMARY KEY,
    city_name   TEXT NOT NULL UNIQUE,
    latitude    DOUBLE PRECISION NOT NULL,
    longitude   DOUBLE PRECISION NOT NULL,
    country     TEXT DEFAULT 'ID',
    timezone    TEXT DEFAULT 'Asia/Jakarta'
);

INSERT INTO raw.city (city_name, latitude, longitude) VALUES
    ('Jakarta',    -6.1750, 106.8650),
    ('Bandung',    -6.9175, 107.6191),
    ('Yogyakarta', -7.7956, 110.3695)
ON CONFLICT (city_name) DO NOTHING;

-- ----------------------------
-- RAW LAYER: Weather Data (append-only)
-- ----------------------------
CREATE TABLE IF NOT EXISTS raw.weather_data (
    id              SERIAL PRIMARY KEY,
    city_id         INT NOT NULL REFERENCES raw.city(city_id),
    temperature_c   DOUBLE PRECISION NOT NULL,
    feels_like_c    DOUBLE PRECISION NOT NULL,
    temp_min_c      DOUBLE PRECISION NOT NULL,
    temp_max_c      DOUBLE PRECISION NOT NULL,
    humidity        SMALLINT NOT NULL CHECK (humidity BETWEEN 0 AND 100),
    pressure_hpa    SMALLINT NOT NULL CHECK (pressure_hpa > 0),
    weather_main    TEXT NOT NULL,
    weather_desc    TEXT NOT NULL,
    wind_speed_ms   DOUBLE PRECISION NOT NULL,
    wind_deg        SMALLINT CHECK (wind_deg BETWEEN 0 AND 360),
    cloud_pct       SMALLINT CHECK (cloud_pct BETWEEN 0 AND 100),
    visibility_m    INT,
    observed_at     TIMESTAMPTZ NOT NULL,
    inserted_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    etl_batch_id    TEXT,
    UNIQUE (city_id, observed_at)
);

CREATE INDEX IF NOT EXISTS idx_weather_observed ON raw.weather_data (observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_weather_city     ON raw.weather_data (city_id);

-- ----------------------------
-- STAGING LAYER
-- ----------------------------
CREATE TABLE IF NOT EXISTS staging.weather_data (
    id              INT PRIMARY KEY,
    city_id         INT NOT NULL,
    city_name       TEXT NOT NULL,
    temperature_c   DOUBLE PRECISION NOT NULL,
    feels_like_c    DOUBLE PRECISION NOT NULL,
    temp_min_c      DOUBLE PRECISION NOT NULL,
    temp_max_c      DOUBLE PRECISION NOT NULL,
    humidity        SMALLINT NOT NULL,
    pressure_hpa    SMALLINT NOT NULL,
    weather_main    TEXT NOT NULL,
    weather_desc    TEXT NOT NULL,
    wind_speed_ms   DOUBLE PRECISION NOT NULL,
    wind_deg        SMALLINT,
    cloud_pct       SMALLINT NOT NULL,
    visibility_m    INT,
    observed_local  TIMESTAMP NOT NULL,
    loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------
-- ANALYTICS LAYER: Daily Weather
-- ----------------------------
CREATE TABLE IF NOT EXISTS analytics.daily_weather (
    city_name         TEXT NOT NULL,
    weather_date      DATE NOT NULL,
    avg_temp_c        NUMERIC(5,2),
    min_temp_c        NUMERIC(5,2),
    max_temp_c        NUMERIC(5,2),
    avg_humidity      SMALLINT,
    avg_pressure      NUMERIC(6,1),
    avg_wind_ms       NUMERIC(4,2),
    observation_count SMALLINT,
    PRIMARY KEY (city_name, weather_date)
);

-- ----------------------------
-- Permissions: grant read to superset
-- ----------------------------
GRANT USAGE ON SCHEMA raw TO superset;
GRANT USAGE ON SCHEMA staging TO superset;
GRANT USAGE ON SCHEMA analytics TO superset;
GRANT SELECT ON ALL TABLES IN SCHEMA raw TO superset;
GRANT SELECT ON ALL TABLES IN SCHEMA staging TO superset;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO superset;
