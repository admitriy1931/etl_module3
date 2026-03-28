"""Centralized configuration loaded from environment variables."""

import os
from pathlib import Path

BASE_DIR = Path(os.getenv("AIRFLOW_HOME", "/opt/airflow"))
DATA_DIR = BASE_DIR / "data"
SAMPLE_DIR = DATA_DIR / "sample"
PROCESSED_DIR = DATA_DIR / "processed"
SQL_DIR = BASE_DIR / "sql"

# --- PostgreSQL ---
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "etl_project")
POSTGRES_USER = os.getenv("POSTGRES_USER", "etl_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "etl_password")

POSTGRES_URI = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# --- MongoDB ---
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB = os.getenv("MONGO_DB", "etl_source")
MONGO_USER = os.getenv("MONGO_USER", "")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")

if MONGO_USER and MONGO_PASSWORD:
    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
else:
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"

# --- Webinar 2 ---
JSON_SOURCE_PATH = os.getenv("JSON_SOURCE_PATH", "")
JSON_SOURCE_URL = os.getenv("JSON_SOURCE_URL", "")
XML_SOURCE_PATH = os.getenv("XML_SOURCE_PATH", "")
XML_SOURCE_URL = os.getenv("XML_SOURCE_URL", "")

# --- Webinar 3 ---
DATASET_PATH = os.getenv("DATASET_PATH", "")
DATASET_URL = os.getenv("DATASET_URL", "")

# --- Webinar 4 ---
INCREMENTAL_DAYS = int(os.getenv("INCREMENTAL_DAYS", "3"))

# --- Final project ---
MONGO_SEED = int(os.getenv("MONGO_SEED", "42"))
MONGO_NUM_USERS = int(os.getenv("MONGO_NUM_USERS", "200"))
MONGO_NUM_SESSIONS = int(os.getenv("MONGO_NUM_SESSIONS", "1000"))
MONGO_NUM_EVENTS = int(os.getenv("MONGO_NUM_EVENTS", "5000"))
MONGO_NUM_TICKETS = int(os.getenv("MONGO_NUM_TICKETS", "500"))
MONGO_NUM_REVIEWS = int(os.getenv("MONGO_NUM_REVIEWS", "800"))
