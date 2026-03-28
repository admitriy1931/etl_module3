"""Build analytical data marts."""

from config.settings import SQL_DIR
from utils.db import get_pg_engine, execute_sql_file
from utils.logger import get_logger

log = get_logger(__name__)


def build_datamarts() -> None:
    """Create / refresh materialized views for analytical data marts."""
    engine = get_pg_engine()
    path = str(SQL_DIR / "ddl" / "final_datamarts.sql")
    execute_sql_file(engine, path)
    log.info("Data marts built / refreshed")


def refresh_datamarts() -> None:
    """Refresh existing materialized views without recreating."""
    engine = get_pg_engine()
    from sqlalchemy import text
    with engine.begin() as conn:
        conn.execute(text("REFRESH MATERIALIZED VIEW mart.dm_user_activity"))
        conn.execute(text("REFRESH MATERIALIZED VIEW mart.dm_support_efficiency"))
    log.info("Materialized views refreshed")
