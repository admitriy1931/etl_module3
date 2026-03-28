"""
DAG: webinar_2_flatten_sources_dag
Flatten nested JSON and XML sources into tabular CSV files.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
}


def task_flatten_json():
    from config.settings import SAMPLE_DIR, PROCESSED_DIR
    from utils.io_helpers import resolve_source
    from webinar_2.flatten_json import flatten_json

    source_path = resolve_source(
        env_path_key="JSON_SOURCE_PATH",
        env_url_key="JSON_SOURCE_URL",
        sample_filename="sample_nested.json",
        sample_dir=SAMPLE_DIR,
    )
    output_dir = str(PROCESSED_DIR / "webinar_2")
    flatten_json(source_path, output_dir)


def task_flatten_xml():
    from config.settings import SAMPLE_DIR, PROCESSED_DIR
    from utils.io_helpers import resolve_source
    from webinar_2.flatten_xml import flatten_xml

    source_path = resolve_source(
        env_path_key="XML_SOURCE_PATH",
        env_url_key="XML_SOURCE_URL",
        sample_filename="sample_nested.xml",
        sample_dir=SAMPLE_DIR,
    )
    output_dir = str(PROCESSED_DIR / "webinar_2")
    flatten_xml(source_path, output_dir)


with DAG(
    dag_id="webinar_2_flatten_sources_dag",
    description="Flatten nested JSON and XML into tabular structures",
    default_args=default_args,
    schedule="@once",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["webinar_2", "flatten"],
) as dag:

    t_json = PythonOperator(
        task_id="flatten_json",
        python_callable=task_flatten_json,
    )

    t_xml = PythonOperator(
        task_id="flatten_xml",
        python_callable=task_flatten_xml,
    )

    t_json >> t_xml
