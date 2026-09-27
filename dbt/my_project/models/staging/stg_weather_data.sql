{{ config(
    materialized="table"
) }}

with source as (
    select
        w.*,
        c.city_name,
        c.latitude,
        c.longitude,
        c.country,
        c.timezone
    from {{ source('raw', 'weather_data') }} w
    join {{ source('raw', 'city') }} c
        on w.city_id = c.city_id
),

de_dup as (
    select *,
        row_number() over (
            partition by city_name, observed_at
            order by inserted_at desc
        ) as rn
    from source
)

select
    id,
    city_id,
    city_name,
    latitude,
    longitude,
    country,
    timezone,
    temperature_c,
    feels_like_c,
    temp_min_c,
    temp_max_c,
    humidity,
    pressure_hpa,
    weather_main,
    weather_desc,
    wind_speed_ms,
    wind_deg,
    cloud_pct,
    visibility_m,
    (observed_at at time zone 'Asia/Jakarta') as observed_local,
    (inserted_at at time zone 'Asia/Jakarta') as loaded_at
from de_dup
where rn = 1
