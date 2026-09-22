{{config(
    materialized="table"
)}}

with stg_data as (
    select * 
    from {{ ref('stg_weather_data') }}
)

select 
    city,
    weather_time_local::date as date_local,
    count(id) as total_observations,
    round(avg(temperature)::numeric, 2) as avg_temperature,
    round(avg(feels_like)::numeric, 2) as avg_feels_like,
    min(temp_min) as min_temperature,
    max(temp_max) as max_temperature,
    round(avg(humidity)::numeric, 2) as avg_humidity,
    round(avg(pressure)::numeric, 2) as avg_pressure,
    round(avg(wind_speed)::numeric, 2) as avg_wind_speed,
    round(avg(clouds)::numeric, 2) as avg_clouds
from stg_data
group by city, weather_time_local::date
order by date_local desc, city asc