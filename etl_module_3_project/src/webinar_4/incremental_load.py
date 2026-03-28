"""Incremental load of weather data into PostgreSQL."""

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from utils.logger import get_logger
from utils.io_helpers import read_csv_file
from utils.db import get_pg_engine, execute_sql_file
from config.settings import PROCESSED_DIR, SQL_DIR, INCREMENTAL_DAYS
from webinar_4.state_manager import get_last_loaded_date, set_last_loaded_date

log = get_logger(__name__)


def run_incremental_load(cleaned_csv_path: str = "", days: int = 0) -> None:
    """
    Incremental load:
    1. Determine the date window (last N days from watermark or from max date)
    2. Filter source data to that window
    3. Load into staging (only the delta)
    4. Upsert into dwh
    5. Update watermark
    """
    engine = get_pg_engine()

    # Ensure tables exist
    ddl_path = str(SQL_DIR / "ddl" / "webinar_4_tables.sql")
    execute_sql_file(engine, ddl_path)

    if days <= 0:
        days = INCREMENTAL_DAYS

    if not cleaned_csv_path:
        cleaned_csv_path = str(PROCESSED_DIR / "webinar_3" / "cleaned_weather.csv")

    if not Path(cleaned_csv_path).exists():
        raise FileNotFoundError(f"Cleaned weather CSV not found: {cleaned_csv_path}")

    df = read_csv_file(cleaned_csv_path)
    df["noted_date"] = pd.to_datetime(df["noted_date"]).dt.date
    df["temp"] = pd.to_numeric(df["temp"])

    # Determine cutoff
    watermark = get_last_loaded_date(engine, "dwh.weather")
    if watermark:
        cutoff_date = watermark - timedelta(days=days)
    else:
        max_date = df["noted_date"].max()
        cutoff_date = max_date - timedelta(days=days)

    log.info("Incremental cutoff date: %s (last %d days)", cutoff_date, days)

    delta = df[df["noted_date"] >= cutoff_date].copy()
    if delta.empty:
        log.info("No new data found for incremental load")
        return

    log.info("Incremental delta: %d rows (from %s)", len(delta), cutoff_date)

    with engine.begin() as conn:
        # Clear staging for the delta window
        conn.execute(
            text("DELETE FROM staging.weather_raw WHERE noted_date >= :cutoff"),
            {"cutoff": cutoff_date},
        )

        # Insert delta into staging
        for _, row in delta.iterrows():
            conn.execute(
                text("""
                    INSERT INTO staging.weather_raw (noted_date, temp, direction)
                    VALUES (:d, :t, :dir)
                """),
                {"d": row["noted_date"], "t": row["temp"], "dir": row.get("out/in", "in")},
            )
        log.info("Inserted %d rows into staging.weather_raw (incremental)", len(delta))

        # Upsert into dwh from staging delta
        conn.execute(text("""
            INSERT INTO dwh.weather (noted_date, temp, direction, loaded_at)
            SELECT DISTINCT noted_date, temp, direction, NOW()
            FROM staging.weather_raw
            WHERE noted_date >= :cutoff
            ON CONFLICT (noted_date, temp, direction) DO UPDATE
                SET loaded_at = NOW()
        """), {"cutoff": cutoff_date})
        log.info("Upsert into dwh.weather complete")

    # Update watermark
    new_max = delta["noted_date"].max()
    set_last_loaded_date(engine, "dwh.weather", new_max)

    log.info("Incremental load finished successfully")
