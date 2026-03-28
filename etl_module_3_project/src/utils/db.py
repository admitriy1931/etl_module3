"""Database connection helpers for PostgreSQL and MongoDB."""

from contextlib import contextmanager
from typing import Generator

import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase

from config.settings import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB,
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_URI,
    MONGO_URI, MONGO_DB,
)
from utils.logger import get_logger

log = get_logger(__name__)


def get_pg_engine() -> Engine:
    """Return a SQLAlchemy engine for the target PostgreSQL database."""
    engine = create_engine(POSTGRES_URI, pool_pre_ping=True, pool_size=5)
    log.info("PostgreSQL engine created: %s:%s/%s", POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB)
    return engine


@contextmanager
def get_pg_connection():
    """Raw psycopg2 connection context manager."""
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )
    try:
        yield conn
    finally:
        conn.close()


def execute_sql_file(engine: Engine, filepath: str) -> None:
    """Execute a SQL file against the engine."""
    log.info("Executing SQL file: %s", filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()
    with engine.begin() as conn:
        for statement in sql.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
    log.info("SQL file executed successfully: %s", filepath)


def get_mongo_client() -> MongoClient:
    """Return a pymongo MongoClient."""
    client = MongoClient(MONGO_URI)
    log.info("MongoDB client created: %s", MONGO_URI)
    return client


def get_mongo_db() -> MongoDatabase:
    """Return the target MongoDB database object."""
    client = get_mongo_client()
    return client[MONGO_DB]
