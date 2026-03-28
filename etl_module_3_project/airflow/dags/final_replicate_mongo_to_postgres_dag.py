"""
DAG: final_replicate_mongo_to_postgres_dag
Extract from MongoDB, transform to relational model, load into PostgreSQL.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def task_create_tables():
    from final_project.ddl import create_all_tables
    create_all_tables()


def task_extract_and_load_sessions():
    from utils.db import get_mongo_db, get_pg_engine
    from final_project.mongo_extract import extract_collection
    from final_project.mongo_transform import transform_sessions
    from final_project.postgres_load import load_sessions

    db = get_mongo_db()
    docs = extract_collection(db, "user_sessions")
    df_sessions, df_pages, df_actions = transform_sessions(docs)
    engine = get_pg_engine()
    load_sessions(engine, df_sessions, df_pages, df_actions)


def task_extract_and_load_events():
    from utils.db import get_mongo_db, get_pg_engine
    from final_project.mongo_extract import extract_collection
    from final_project.mongo_transform import transform_events
    from final_project.postgres_load import load_events

    db = get_mongo_db()
    docs = extract_collection(db, "event_logs")
    df_events = transform_events(docs)
    engine = get_pg_engine()
    load_events(engine, df_events)


def task_extract_and_load_tickets():
    from utils.db import get_mongo_db, get_pg_engine
    from final_project.mongo_extract import extract_collection
    from final_project.mongo_transform import transform_tickets
    from final_project.postgres_load import load_tickets

    db = get_mongo_db()
    docs = extract_collection(db, "support_tickets")
    df_tickets, df_messages = transform_tickets(docs)
    engine = get_pg_engine()
    load_tickets(engine, df_tickets, df_messages)


def task_extract_and_load_recommendations():
    from utils.db import get_mongo_db, get_pg_engine
    from final_project.mongo_extract import extract_collection
    from final_project.mongo_transform import transform_recommendations
    from final_project.postgres_load import load_recommendations

    db = get_mongo_db()
    docs = extract_collection(db, "user_recommendations")
    df_recs, df_prods = transform_recommendations(docs)
    engine = get_pg_engine()
    load_recommendations(engine, df_recs, df_prods)


def task_extract_and_load_moderation():
    from utils.db import get_mongo_db, get_pg_engine
    from final_project.mongo_extract import extract_collection
    from final_project.mongo_transform import transform_moderation
    from final_project.postgres_load import load_moderation

    db = get_mongo_db()
    docs = extract_collection(db, "moderation_queue")
    df_reviews, df_flags = transform_moderation(docs)
    engine = get_pg_engine()
    load_moderation(engine, df_reviews, df_flags)


def task_promote_to_dwh():
    from utils.db import get_pg_engine
    from final_project.postgres_load import promote_staging_to_dwh

    engine = get_pg_engine()
    promote_staging_to_dwh(engine)


with DAG(
    dag_id="final_replicate_mongo_to_postgres_dag",
    description="Replicate MongoDB data to PostgreSQL staging, then promote to DWH",
    default_args=default_args,
    schedule="@once",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["final", "replicate", "mongo", "postgres"],
) as dag:

    t_ddl = PythonOperator(task_id="create_tables", python_callable=task_create_tables)

    t_sessions = PythonOperator(task_id="load_sessions", python_callable=task_extract_and_load_sessions)
    t_events = PythonOperator(task_id="load_events", python_callable=task_extract_and_load_events)
    t_tickets = PythonOperator(task_id="load_tickets", python_callable=task_extract_and_load_tickets)
    t_recs = PythonOperator(task_id="load_recommendations", python_callable=task_extract_and_load_recommendations)
    t_moder = PythonOperator(task_id="load_moderation", python_callable=task_extract_and_load_moderation)

    t_promote = PythonOperator(task_id="promote_to_dwh", python_callable=task_promote_to_dwh)

    t_ddl >> [t_sessions, t_events, t_tickets, t_recs, t_moder] >> t_promote
