{{ config(
    materialized="table",
    unique_key="id"
) }}

with stg_data as (
    select * 
    from {{ ref('stg_weather_data') }}
)

select
    id,
    city,
    lat,
    lon,
    temperature,
    feels_like,
    temp_min,
    temp_max,
    humidity,
    pressure,
    weather_main,
    weather_description,
    wind_speed,
    wind_deg,
    clouds,
    visibility,
    weather_time_local
from stg_data