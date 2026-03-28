"""
DAG: webinar_4_load_to_postgres_dag
Load cleaned weather data into PostgreSQL in two modes:
  - full_historical_load: truncate + reload everything
  - incremental_load: load only last N days
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
}


def task_full_load():
    from webinar_4.full_load import run_full_load
    run_full_load()


def task_incremental_load():
    from webinar_4.incremental_load import run_incremental_load
    run_incremental_load()


with DAG(
    dag_id="webinar_4_load_to_postgres_dag",
    description="Load weather data into PostgreSQL: full historical + incremental",
    default_args=default_args,
    schedule="@once",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["webinar_4", "load", "postgres"],
) as dag:

    t_full = PythonOperator(
        task_id="full_historical_load",
        python_callable=task_full_load,
    )

    t_incr = PythonOperator(
        task_id="incremental_load",
        python_callable=task_incremental_load,
    )

    t_full >> t_incr
