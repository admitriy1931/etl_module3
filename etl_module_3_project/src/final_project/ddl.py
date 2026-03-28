"""Execute DDL scripts for the final project."""

from config.settings import SQL_DIR
from utils.db import get_pg_engine, execute_sql_file
from utils.logger import get_logger

log = get_logger(__name__)


def create_staging_tables() -> None:
    """Create all staging schema tables."""
    engine = get_pg_engine()
    path = str(SQL_DIR / "ddl" / "final_staging_tables.sql")
    execute_sql_file(engine, path)
    log.info("Staging tables created")


def create_dwh_tables() -> None:
    """Create all DWH schema tables."""
    engine = get_pg_engine()
    path = str(SQL_DIR / "ddl" / "final_dwh_tables.sql")
    execute_sql_file(engine, path)
    log.info("DWH tables created")


def create_all_tables() -> None:
    """Create staging + DWH tables."""
    create_staging_tables()
    create_dwh_tables()
    log.info("All final project tables created")
