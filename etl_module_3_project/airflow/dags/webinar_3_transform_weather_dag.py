"""
DAG: webinar_3_transform_weather_dag
Transform the temperature dataset: filter, parse dates, remove outliers,
produce cleaned dataset, hottest 5 and coldest 5 days.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
}


def task_transform_weather():
    from config.settings import SAMPLE_DIR, PROCESSED_DIR
    from utils.io_helpers import resolve_source
    from webinar_3.transform_weather import transform_weather

    source_path = resolve_source(
        env_path_key="DATASET_PATH",
        env_url_key="DATASET_URL",
        sample_filename="sample_temperature.csv",
        sample_dir=SAMPLE_DIR,
    )
    output_dir = str(PROCESSED_DIR / "webinar_3")
    transform_weather(source_path, output_dir)


with DAG(
    dag_id="webinar_3_transform_weather_dag",
    description="Transform temperature dataset: filter, clean, compute hottest/coldest days",
    default_args=default_args,
    schedule="@once",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["webinar_3", "transform", "weather"],
) as dag:

    t_transform = PythonOperator(
        task_id="transform_weather",
        python_callable=task_transform_weather,
    )
