"""
DAG: final_build_datamarts_dag
Build analytical data marts (materialized views) from DWH data.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
}


def task_build_datamarts():
    from final_project.datamarts import build_datamarts
    build_datamarts()


with DAG(
    dag_id="final_build_datamarts_dag",
    description="Build dm_user_activity and dm_support_efficiency materialized views",
    default_args=default_args,
    schedule="@once",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["final", "datamarts", "analytics"],
) as dag:

    t_build = PythonOperator(
        task_id="build_datamarts",
        python_callable=task_build_datamarts,
    )
