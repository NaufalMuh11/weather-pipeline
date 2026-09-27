{{ config(
    materialized="table"
) }}

with stg_data as (
    select *
    from {{ ref('stg_weather_data') }}
)

select
    city_name,
    observed_local::date as weather_date,
    round(avg(temperature_c)::numeric, 2) as avg_temp_c,
    round(min(temp_min_c)::numeric, 2) as min_temp_c,
    round(max(temp_max_c)::numeric, 2) as max_temp_c,
    round(avg(humidity)::numeric) as avg_humidity,
    round(avg(pressure_hpa)::numeric, 1) as avg_pressure,
    round(avg(wind_speed_ms)::numeric, 2) as avg_wind_ms,
    count(id) as observation_count
from stg_data
group by city_name, observed_local::date
