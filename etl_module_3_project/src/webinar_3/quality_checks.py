"""Data quality checks for the weather dataset."""

import pandas as pd

from utils.logger import get_logger

log = get_logger(__name__)

REQUIRED_COLUMNS = {"noted_date", "temp", "out/in"}


def validate_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure required columns exist and types are convertible."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    log.info("Schema validation passed. Columns: %s", list(df.columns))
    return df


def validate_not_empty(df: pd.DataFrame, label: str = "dataset") -> pd.DataFrame:
    """Raise if DataFrame is empty."""
    if df.empty:
        raise ValueError(f"The {label} is empty after processing.")
    log.info("Non-empty check passed for '%s': %d rows", label, len(df))
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate rows."""
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    if removed > 0:
        log.info("Removed %d duplicate rows", removed)
    return df


def remove_outliers_by_percentile(
    df: pd.DataFrame,
    column: str,
    lower_pct: float = 0.05,
    upper_pct: float = 0.95,
) -> pd.DataFrame:
    """Remove rows where column value is outside [lower_pct, upper_pct] percentiles."""
    lower_bound = df[column].quantile(lower_pct)
    upper_bound = df[column].quantile(upper_pct)
    before = len(df)
    df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)].copy()
    removed = before - len(df)
    log.info(
        "Outlier removal on '%s': bounds [%.2f, %.2f], removed %d rows",
        column, lower_bound, upper_bound, removed,
    )
    return df
