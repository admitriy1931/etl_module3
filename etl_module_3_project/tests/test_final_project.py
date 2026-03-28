"""Tests for the Final Project: data generation, transform, datamarts modules."""

import sys
from pathlib import Path

import pytest
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from final_project.mongo_transform import (
    transform_sessions,
    transform_events,
    transform_tickets,
    transform_recommendations,
    transform_moderation,
)


SAMPLE_SESSION_DOCS = [
    {
        "session_id": "sess_001",
        "user_id": "user_001",
        "start_time": "2024-01-10T09:00:00Z",
        "end_time": "2024-01-10T09:30:00Z",
        "pages_visited": ["/home", "/products", "/cart"],
        "device": "mobile",
        "actions": ["login", "view_product", "add_to_cart"],
    },
    {
        "session_id": "sess_002",
        "user_id": "user_002",
        "start_time": "2024-01-11T10:00:00Z",
        "end_time": "2024-01-11T10:45:00Z",
        "pages_visited": ["/home", "/blog"],
        "device": "desktop",
        "actions": ["login", "scroll"],
    },
    {
        "session_id": "sess_001",
        "user_id": "user_001",
        "start_time": "2024-01-10T09:00:00Z",
        "end_time": "2024-01-10T09:30:00Z",
        "pages_visited": ["/home", "/products", "/cart"],
        "device": "mobile",
        "actions": ["login", "view_product", "add_to_cart"],
    },
]

SAMPLE_EVENT_DOCS = [
    {"event_id": "evt_001", "timestamp": "2024-01-10T09:05:00Z", "event_type": "click", "details": {"page": "/products"}},
    {"event_id": "evt_002", "timestamp": "2024-01-10T09:06:00Z", "event_type": "page_view", "details": {"page": "/home"}},
    {"event_id": "evt_001", "timestamp": "2024-01-10T09:05:00Z", "event_type": "click", "details": {"page": "/products"}},
]

SAMPLE_TICKET_DOCS = [
    {
        "ticket_id": "ticket_001",
        "user_id": "user_001",
        "status": "open",
        "issue_type": "payment",
        "messages": [
            {"sender": "user", "message": "Cannot pay.", "timestamp": "2024-01-09T12:00:00Z"},
            {"sender": "support", "message": "Please specify payment method.", "timestamp": "2024-01-09T13:00:00Z"},
        ],
        "created_at": "2024-01-09T11:55:00Z",
        "updated_at": "2024-01-09T13:00:00Z",
    },
]

SAMPLE_RECS_DOCS = [
    {"user_id": "user_001", "recommended_products": ["prod_101", "prod_205"], "last_updated": "2024-01-10T08:00:00Z"},
    {"user_id": "user_001", "recommended_products": ["prod_101", "prod_205"], "last_updated": "2024-01-10T08:00:00Z"},
]

SAMPLE_MODERATION_DOCS = [
    {
        "review_id": "rev_001",
        "user_id": "user_001",
        "product_id": "prod_101",
        "review_text": "Great product!",
        "rating": 5,
        "moderation_status": "pending",
        "flags": ["contains_images"],
        "submitted_at": "2024-01-08T10:20:00Z",
    },
]


class TestTransformSessions:
    def test_dedup(self):
        df_s, df_p, df_a = transform_sessions(SAMPLE_SESSION_DOCS)
        assert len(df_s) == 2

    def test_pages_linked(self):
        df_s, df_p, df_a = transform_sessions(SAMPLE_SESSION_DOCS)
        assert set(df_p["session_id"]).issubset(set(df_s["session_id"]))

    def test_actions_linked(self):
        df_s, df_p, df_a = transform_sessions(SAMPLE_SESSION_DOCS)
        assert set(df_a["session_id"]).issubset(set(df_s["session_id"]))


class TestTransformEvents:
    def test_dedup(self):
        df = transform_events(SAMPLE_EVENT_DOCS)
        assert len(df) == 2

    def test_columns(self):
        df = transform_events(SAMPLE_EVENT_DOCS)
        assert "event_id" in df.columns
        assert "event_type" in df.columns


class TestTransformTickets:
    def test_transform(self):
        df_t, df_m = transform_tickets(SAMPLE_TICKET_DOCS)
        assert len(df_t) == 1
        assert len(df_m) == 2


class TestTransformRecommendations:
    def test_dedup(self):
        df_r, df_p = transform_recommendations(SAMPLE_RECS_DOCS)
        assert len(df_r) == 1


class TestTransformModeration:
    def test_transform(self):
        df_rev, df_flags = transform_moderation(SAMPLE_MODERATION_DOCS)
        assert len(df_rev) == 1
        assert len(df_flags) == 1


class TestModuleImports:
    def test_generate_mongo_data(self):
        from final_project.generate_mongo_data import generate_all
        assert callable(generate_all)

    def test_datamarts(self):
        from final_project.datamarts import build_datamarts
        assert callable(build_datamarts)

    def test_ddl(self):
        from final_project.ddl import create_all_tables
        assert callable(create_all_tables)

    def test_postgres_load(self):
        from final_project.postgres_load import promote_staging_to_dwh
        assert callable(promote_staging_to_dwh)
