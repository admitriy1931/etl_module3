"""Watermark / state management for incremental loads."""

from datetime import date, timedelta
from typing import Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine

from utils.logger import get_logger

log = get_logger(__name__)


def get_last_loaded_date(engine: Engine, table_name: str) -> Optional[date]:
    """Read the last loaded date watermark for a table."""
    query = text(
        "SELECT last_loaded_date FROM staging.load_state WHERE table_name = :tbl"
    )
    with engine.connect() as conn:
        row = conn.execute(query, {"tbl": table_name}).fetchone()
    if row and row[0]:
        log.info("Last loaded date for '%s': %s", table_name, row[0])
        return row[0]
    log.info("No watermark found for '%s'", table_name)
    return None


def set_last_loaded_date(engine: Engine, table_name: str, loaded_date: date) -> None:
    """Upsert the watermark for a table."""
    upsert = text("""
        INSERT INTO staging.load_state (table_name, last_loaded_date, updated_at)
        VALUES (:tbl, :dt, NOW())
        ON CONFLICT (table_name)
        DO UPDATE SET last_loaded_date = :dt, updated_at = NOW()
    """)
    with engine.begin() as conn:
        conn.execute(upsert, {"tbl": table_name, "dt": loaded_date})
    log.info("Watermark updated for '%s': %s", table_name, loaded_date)
