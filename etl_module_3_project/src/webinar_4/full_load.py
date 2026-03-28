"""Full historical load of weather data into PostgreSQL."""

from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from utils.logger import get_logger
from utils.io_helpers import read_csv_file
from utils.db import get_pg_engine, execute_sql_file
from config.settings import PROCESSED_DIR, SQL_DIR
from webinar_4.state_manager import set_last_loaded_date

log = get_logger(__name__)


def run_full_load(cleaned_csv_path: str = "") -> None:
    """
    Full historical load:
    1. Create tables if not exist
    2. Truncate staging + target
    3. Load all data into staging
    4. Deduplicate and insert into dwh
    5. Update watermark
    """
    engine = get_pg_engine()

    # Ensure tables exist
    ddl_path = str(SQL_DIR / "ddl" / "webinar_4_tables.sql")
    execute_sql_file(engine, ddl_path)

    # Resolve input file
    if not cleaned_csv_path:
        cleaned_csv_path = str(PROCESSED_DIR / "webinar_3" / "cleaned_weather.csv")

    if not Path(cleaned_csv_path).exists():
        raise FileNotFoundError(f"Cleaned weather CSV not found: {cleaned_csv_path}")

    df = read_csv_file(cleaned_csv_path)
    df["noted_date"] = pd.to_datetime(df["noted_date"]).dt.date
    df["temp"] = pd.to_numeric(df["temp"])
    log.info("Loaded %d rows for full historical load", len(df))

    with engine.begin() as conn:
        # Truncate both layers
        conn.execute(text("TRUNCATE TABLE staging.weather_raw RESTART IDENTITY"))
        conn.execute(text("TRUNCATE TABLE dwh.weather RESTART IDENTITY"))
        log.info("Truncated staging.weather_raw and dwh.weather")

        # Load into staging
        for _, row in df.iterrows():
            conn.execute(
                text("""
                    INSERT INTO staging.weather_raw (noted_date, temp, direction)
                    VALUES (:d, :t, :dir)
                """),
                {"d": row["noted_date"], "t": row["temp"], "dir": row.get("out/in", "in")},
            )
        log.info("Inserted %d rows into staging.weather_raw", len(df))

        # Deduplicate and load into dwh
        conn.execute(text("""
            INSERT INTO dwh.weather (noted_date, temp, direction, loaded_at)
            SELECT DISTINCT noted_date, temp, direction, NOW()
            FROM staging.weather_raw
            ON CONFLICT (noted_date, temp, direction) DO NOTHING
        """))
        log.info("Full load into dwh.weather complete")

    # Update watermark
    if not df.empty:
        max_date = df["noted_date"].max()
        set_last_loaded_date(engine, "dwh.weather", max_date)

    log.info("Full historical load finished successfully")
