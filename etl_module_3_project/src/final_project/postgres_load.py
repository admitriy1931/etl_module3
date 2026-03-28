"""Load transformed DataFrames into PostgreSQL staging and DWH layers."""

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from utils.logger import get_logger
from utils.db import get_pg_engine
from final_project.ddl import create_all_tables

log = get_logger(__name__)


def _truncate_table(engine: Engine, schema: str, table: str) -> None:
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {schema}.{table} RESTART IDENTITY CASCADE"))
    log.info("Truncated %s.%s", schema, table)


def _load_df(engine: Engine, df: pd.DataFrame, schema: str, table: str) -> None:
    if df.empty:
        log.warning("Skipping empty DataFrame for %s.%s", schema, table)
        return
    df.to_sql(table, engine, schema=schema, if_exists="append", index=False, method="multi")
    log.info("Loaded %d rows into %s.%s", len(df), schema, table)


def load_sessions(engine: Engine, df_sessions: pd.DataFrame, df_pages: pd.DataFrame, df_actions: pd.DataFrame) -> None:
    _truncate_table(engine, "staging", "session_actions")
    _truncate_table(engine, "staging", "session_pages")
    _truncate_table(engine, "staging", "sessions")
    _load_df(engine, df_sessions, "staging", "sessions")
    _load_df(engine, df_pages, "staging", "session_pages")
    _load_df(engine, df_actions, "staging", "session_actions")


def load_events(engine: Engine, df_events: pd.DataFrame) -> None:
    _truncate_table(engine, "staging", "events")
    _load_df(engine, df_events, "staging", "events")


def load_tickets(engine: Engine, df_tickets: pd.DataFrame, df_messages: pd.DataFrame) -> None:
    _truncate_table(engine, "staging", "ticket_messages")
    _truncate_table(engine, "staging", "tickets")
    _load_df(engine, df_tickets, "staging", "tickets")
    _load_df(engine, df_messages, "staging", "ticket_messages")


def load_recommendations(engine: Engine, df_recs: pd.DataFrame, df_prods: pd.DataFrame) -> None:
    _truncate_table(engine, "staging", "recommendation_products")
    _truncate_table(engine, "staging", "recommendations")
    _load_df(engine, df_recs, "staging", "recommendations")
    _load_df(engine, df_prods, "staging", "recommendation_products")


def load_moderation(engine: Engine, df_reviews: pd.DataFrame, df_flags: pd.DataFrame) -> None:
    _truncate_table(engine, "staging", "moderation_flags")
    _truncate_table(engine, "staging", "moderation_reviews")
    _load_df(engine, df_reviews, "staging", "moderation_reviews")
    _load_df(engine, df_flags, "staging", "moderation_flags")


def promote_staging_to_dwh(engine: Engine) -> None:
    """Copy all data from staging to DWH with deduplication via upsert."""
    upserts = [
        (
            "dwh.sessions",
            """INSERT INTO dwh.sessions (session_id, user_id, start_time, end_time, device, loaded_at)
               SELECT session_id, user_id, start_time, end_time, device, NOW()
               FROM staging.sessions
               ON CONFLICT (session_id) DO UPDATE SET
                   user_id = EXCLUDED.user_id,
                   start_time = EXCLUDED.start_time,
                   end_time = EXCLUDED.end_time,
                   device = EXCLUDED.device,
                   loaded_at = NOW()""",
        ),
        (
            "dwh.session_pages",
            """DELETE FROM dwh.session_pages WHERE session_id IN (SELECT session_id FROM staging.sessions);
               INSERT INTO dwh.session_pages (session_id, page_url, page_order)
               SELECT session_id, page_url, page_order FROM staging.session_pages""",
        ),
        (
            "dwh.session_actions",
            """DELETE FROM dwh.session_actions WHERE session_id IN (SELECT session_id FROM staging.sessions);
               INSERT INTO dwh.session_actions (session_id, action_name, action_order)
               SELECT session_id, action_name, action_order FROM staging.session_actions""",
        ),
        (
            "dwh.events",
            """INSERT INTO dwh.events (event_id, event_timestamp, event_type, details, loaded_at)
               SELECT event_id, event_timestamp, event_type, details, NOW()
               FROM staging.events
               ON CONFLICT (event_id, event_timestamp) DO UPDATE SET
                   event_type = EXCLUDED.event_type,
                   details = EXCLUDED.details,
                   loaded_at = NOW()""",
        ),
        (
            "dwh.tickets",
            """INSERT INTO dwh.tickets (ticket_id, user_id, status, issue_type, created_at, updated_at, loaded_at)
               SELECT ticket_id, user_id, status, issue_type, created_at, updated_at, NOW()
               FROM staging.tickets
               ON CONFLICT (ticket_id) DO UPDATE SET
                   status = EXCLUDED.status,
                   issue_type = EXCLUDED.issue_type,
                   updated_at = EXCLUDED.updated_at,
                   loaded_at = NOW()""",
        ),
        (
            "dwh.ticket_messages",
            """DELETE FROM dwh.ticket_messages WHERE ticket_id IN (SELECT ticket_id FROM staging.tickets);
               INSERT INTO dwh.ticket_messages (ticket_id, sender, message, msg_timestamp, msg_order)
               SELECT ticket_id, sender, message, msg_timestamp, msg_order FROM staging.ticket_messages""",
        ),
        (
            "dwh.recommendations",
            """INSERT INTO dwh.recommendations (user_id, last_updated, loaded_at)
               SELECT user_id, last_updated, NOW()
               FROM staging.recommendations
               ON CONFLICT (user_id) DO UPDATE SET
                   last_updated = EXCLUDED.last_updated,
                   loaded_at = NOW()""",
        ),
        (
            "dwh.recommendation_products",
            """DELETE FROM dwh.recommendation_products WHERE user_id IN (SELECT user_id FROM staging.recommendations);
               INSERT INTO dwh.recommendation_products (user_id, product_id, product_order)
               SELECT user_id, product_id, product_order FROM staging.recommendation_products""",
        ),
        (
            "dwh.moderation_reviews",
            """INSERT INTO dwh.moderation_reviews (review_id, user_id, product_id, review_text, rating, moderation_status, submitted_at, loaded_at)
               SELECT review_id, user_id, product_id, review_text, rating, moderation_status, submitted_at, NOW()
               FROM staging.moderation_reviews
               ON CONFLICT (review_id) DO UPDATE SET
                   moderation_status = EXCLUDED.moderation_status,
                   loaded_at = NOW()""",
        ),
        (
            "dwh.moderation_flags",
            """DELETE FROM dwh.moderation_flags WHERE review_id IN (SELECT review_id FROM staging.moderation_reviews);
               INSERT INTO dwh.moderation_flags (review_id, flag_name)
               SELECT review_id, flag_name FROM staging.moderation_flags""",
        ),
    ]

    with engine.begin() as conn:
        for target, sql in upserts:
            for stmt in sql.split(";"):
                stmt = stmt.strip()
                if stmt:
                    conn.execute(text(stmt))
            log.info("Promoted data to %s", target)

    log.info("All staging data promoted to DWH")
