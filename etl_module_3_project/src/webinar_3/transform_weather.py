"""Transform the temperature dataset per Webinar 3 requirements."""

from pathlib import Path

import pandas as pd

from utils.logger import get_logger
from utils.io_helpers import read_csv_file, save_dataframe
from utils.date_helpers import normalize_date_column
from webinar_3.quality_checks import (
    validate_schema, validate_not_empty, remove_duplicates,
    remove_outliers_by_percentile,
)

log = get_logger(__name__)


def transform_weather(input_path: str, output_dir: str) -> dict:
    """
    Full transformation pipeline:
    1. Read CSV
    2. Validate schema
    3. Remove duplicates
    4. Filter out/in = 'in'
    5. Parse noted_date to yyyy-MM-dd
    6. Convert temp to numeric
    7. Remove outliers by 5th/95th percentile
    8. Compute hottest 5 days
    9. Compute coldest 5 days
    10. Save all artifacts
    """
    df = read_csv_file(input_path)
    validate_schema(df)
    df = remove_duplicates(df)

    # Filter direction
    before_filter = len(df)
    df = df[df["out/in"].str.strip().str.lower() == "in"].copy()
    log.info("Filtered out/in='in': %d -> %d rows", before_filter, len(df))
    validate_not_empty(df, "filtered dataset")

    # Parse date
    df = normalize_date_column(df, "noted_date")
    validate_not_empty(df, "after date parsing")

    # Convert temp to numeric
    df["temp"] = pd.to_numeric(df["temp"], errors="coerce")
    df = df.dropna(subset=["temp"]).copy()
    validate_not_empty(df, "after numeric temp conversion")

    # Remove outliers
    df_cleaned = remove_outliers_by_percentile(df, "temp", 0.05, 0.95)
    validate_not_empty(df_cleaned, "cleaned dataset")

    # Sort by date
    df_cleaned = df_cleaned.sort_values("noted_date").reset_index(drop=True)

    # Hottest 5 days
    hottest_5 = df_cleaned.nlargest(5, "temp")[["noted_date", "temp"]].reset_index(drop=True)
    log.info("Hottest 5 days:\n%s", hottest_5.to_string(index=False))

    # Coldest 5 days
    coldest_5 = df_cleaned.nsmallest(5, "temp")[["noted_date", "temp"]].reset_index(drop=True)
    log.info("Coldest 5 days:\n%s", coldest_5.to_string(index=False))

    # Save artifacts
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    save_dataframe(df_cleaned, str(out / "cleaned_weather.csv"))
    save_dataframe(hottest_5, str(out / "hottest_5_days.csv"))
    save_dataframe(coldest_5, str(out / "coldest_5_days.csv"))

    return {
        "cleaned": df_cleaned,
        "hottest_5": hottest_5,
        "coldest_5": coldest_5,
        "cleaned_path": str(out / "cleaned_weather.csv"),
    }
