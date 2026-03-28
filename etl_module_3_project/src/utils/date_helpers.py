"""Date parsing and formatting helpers."""

import re
from datetime import datetime, date
from typing import Optional

import pandas as pd

from utils.logger import get_logger

log = get_logger(__name__)

DATE_PATTERNS = [
    (re.compile(r"^\d{2}-\d{2}-\d{4}$"), "%d-%m-%Y"),
    (re.compile(r"^\d{4}-\d{2}-\d{2}$"), "%Y-%m-%d"),
    (re.compile(r"^\d{2}/\d{2}/\d{4}$"), "%d/%m/%Y"),
    (re.compile(r"^\d{4}/\d{2}/\d{2}$"), "%Y/%m/%d"),
    (re.compile(r"^\d{2}\.\d{2}\.\d{4}$"), "%d.%m.%Y"),
]


def parse_date(value: str) -> Optional[date]:
    """Try multiple date patterns and return a date object."""
    value = value.strip()
    for pattern, fmt in DATE_PATTERNS:
        if pattern.match(value):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def normalize_date_column(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Convert a date column to yyyy-MM-dd date type."""
    df = df.copy()
    df[col] = df[col].apply(lambda x: parse_date(str(x)) if pd.notna(x) else None)
    df[col] = pd.to_datetime(df[col])
    invalid_count = df[col].isna().sum()
    if invalid_count > 0:
        log.warning("Dropped %d rows with unparseable dates in column '%s'", invalid_count, col)
        df = df.dropna(subset=[col])
    return df
