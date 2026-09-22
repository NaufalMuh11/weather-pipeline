{{ config(
    materialized="table"
) }}

with source as (
    select *
    from {{ source('dev', 'raw_weather_data') }}
),

de_dup as (
    select *,
    row_number() over (partition by id order by inserted_at desc) as rn
    from source
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
    observed_at as weather_time_local,
    (inserted_at at time zone 'UTC' at time zone 'Asia/Jakarta') as inserted_at_local
from de_dup
where rn = 1