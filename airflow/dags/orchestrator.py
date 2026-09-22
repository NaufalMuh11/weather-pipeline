import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.standard.operators.python import PythonOperator
from docker.types import Mount

HOST_PROJECT_PATH = os.getenv("HOST_PROJECT_PATH", "E:/Work/Project/Data_Project/weather-data-engineer")


def _ingest_data(**_kwargs):
    """Import insert_records only at task runtime, not at DAG parse time."""
    sys.path.insert(0, '/opt/airflow/api-request')
    from insert_records import main
    main()


default_args = {
    'description': 'A DAG to orchestrate weather data ingestion and dbt transformation.',
    'start_date': datetime(2026, 9, 19),
    'catchup': False,
}

with DAG(
    dag_id='weather-api-dbt-orchestrator',
    default_args=default_args,
    schedule='@hourly',
    tags=['weather', 'etl'],
    catchup=False,
) as dag:
    task1 = PythonOperator(
        task_id='ingest_data_task',
        python_callable=_ingest_data,
    )

    task2 = DockerOperator(
        task_id='transform_data_task',
        image='ghcr.io/dbt-labs/dbt-postgres:1.9.latest',
        command='run',
        working_dir='/usr/app',
        mounts=[
            Mount(
                source=f'{HOST_PROJECT_PATH}/dbt/my_project',
                target='/usr/app',
                type='bind',
            ),
            Mount(
                source=f'{HOST_PROJECT_PATH}/dbt/profiles.yml',
                target='/root/.dbt/profiles.yml',
                type='bind',
            ),
        ],
        network_mode='weather-data-engineer_my-network',
        docker_url='unix://var/run/docker.sock',
        auto_remove='success',
        mount_tmp_dir=False,
        environment={
            'POSTGRES_USER': os.getenv('POSTGRES_USER', 'user_d'),
            'POSTGRES_PASSWORD': os.getenv('POSTGRES_PASSWORD', 'admin123'),
        },
    )

    task1 >> task2
