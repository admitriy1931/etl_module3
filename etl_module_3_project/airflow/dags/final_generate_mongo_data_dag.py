"""
DAG: final_generate_mongo_data_dag
Generate realistic data and populate MongoDB collections.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
}


def task_generate_data():
    from utils.db import get_mongo_db
    from final_project.generate_mongo_data import generate_all

    db = get_mongo_db()
    counts = generate_all(db)
    return counts


with DAG(
    dag_id="final_generate_mongo_data_dag",
    description="Generate realistic data and insert into MongoDB",
    default_args=default_args,
    schedule="@once",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["final", "mongo", "generate"],
) as dag:

    t_generate = PythonOperator(
        task_id="generate_mongo_data",
        python_callable=task_generate_data,
    )
