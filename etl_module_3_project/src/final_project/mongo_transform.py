"""Transform MongoDB documents into relational DataFrames."""

from typing import Dict, List, Any, Tuple

import pandas as pd

from utils.logger import get_logger

log = get_logger(__name__)


def transform_sessions(docs: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Normalize user_sessions into sessions, session_pages, session_actions."""
    sessions_rows = []
    pages_rows = []
    actions_rows = []

    seen_sessions = set()

    for doc in docs:
        sid = doc["session_id"]
        if sid in seen_sessions:
            continue
        seen_sessions.add(sid)

        sessions_rows.append({
            "session_id": sid,
            "user_id": doc["user_id"],
            "start_time": doc["start_time"],
            "end_time": doc.get("end_time"),
            "device": doc.get("device", ""),
        })

        for i, page in enumerate(doc.get("pages_visited", [])):
            pages_rows.append({
                "session_id": sid,
                "page_url": page,
                "page_order": i + 1,
            })

        for i, action in enumerate(doc.get("actions", [])):
            actions_rows.append({
                "session_id": sid,
                "action_name": action,
                "action_order": i + 1,
            })

    df_sessions = pd.DataFrame(sessions_rows)
    df_pages = pd.DataFrame(pages_rows)
    df_actions = pd.DataFrame(actions_rows)

    log.info(
        "Transformed sessions: %d sessions, %d pages, %d actions",
        len(df_sessions), len(df_pages), len(df_actions),
    )
    return df_sessions, df_pages, df_actions


def transform_events(docs: List[Dict[str, Any]]) -> pd.DataFrame:
    """Normalize event_logs into a flat events table."""
    rows = []
    seen = set()
    for doc in docs:
        eid = doc["event_id"]
        if eid in seen:
            continue
        seen.add(eid)
        details = doc.get("details")
        if isinstance(details, dict):
            details_str = str(details)
        elif isinstance(details, str):
            details_str = details
        else:
            details_str = str(details) if details else ""
        rows.append({
            "event_id": eid,
            "event_timestamp": doc["timestamp"],
            "event_type": doc["event_type"],
            "details": details_str,
        })
    df = pd.DataFrame(rows)
    log.info("Transformed %d events", len(df))
    return df


def transform_tickets(docs: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Normalize support_tickets into tickets and ticket_messages."""
    tickets_rows = []
    messages_rows = []
    seen = set()

    for doc in docs:
        tid = doc["ticket_id"]
        if tid in seen:
            continue
        seen.add(tid)

        tickets_rows.append({
            "ticket_id": tid,
            "user_id": doc["user_id"],
            "status": doc["status"],
            "issue_type": doc["issue_type"],
            "created_at": doc["created_at"],
            "updated_at": doc.get("updated_at"),
        })

        for i, msg in enumerate(doc.get("messages", [])):
            messages_rows.append({
                "ticket_id": tid,
                "sender": msg.get("sender", ""),
                "message": msg.get("message", ""),
                "msg_timestamp": msg.get("timestamp"),
                "msg_order": i + 1,
            })

    df_tickets = pd.DataFrame(tickets_rows)
    df_messages = pd.DataFrame(messages_rows)
    log.info("Transformed %d tickets, %d messages", len(df_tickets), len(df_messages))
    return df_tickets, df_messages


def transform_recommendations(docs: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Normalize user_recommendations into recommendations and recommendation_products."""
    recs_rows = []
    products_rows = []
    seen = set()

    for doc in docs:
        uid = doc["user_id"]
        if uid in seen:
            continue
        seen.add(uid)

        recs_rows.append({
            "user_id": uid,
            "last_updated": doc.get("last_updated"),
        })

        for i, prod in enumerate(doc.get("recommended_products", [])):
            products_rows.append({
                "user_id": uid,
                "product_id": prod,
                "product_order": i + 1,
            })

    df_recs = pd.DataFrame(recs_rows)
    df_prods = pd.DataFrame(products_rows)
    log.info("Transformed %d recommendations, %d product links", len(df_recs), len(df_prods))
    return df_recs, df_prods


def transform_moderation(docs: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Normalize moderation_queue into moderation_reviews and moderation_flags."""
    reviews_rows = []
    flags_rows = []
    seen = set()

    for doc in docs:
        rid = doc["review_id"]
        if rid in seen:
            continue
        seen.add(rid)

        reviews_rows.append({
            "review_id": rid,
            "user_id": doc["user_id"],
            "product_id": doc["product_id"],
            "review_text": doc.get("review_text", ""),
            "rating": doc.get("rating"),
            "moderation_status": doc["moderation_status"],
            "submitted_at": doc["submitted_at"],
        })

        for flag in doc.get("flags", []):
            flags_rows.append({
                "review_id": rid,
                "flag_name": flag,
            })

    df_reviews = pd.DataFrame(reviews_rows)
    df_flags = pd.DataFrame(flags_rows)
    log.info("Transformed %d moderation reviews, %d flags", len(df_reviews), len(df_flags))
    return df_reviews, df_flags
