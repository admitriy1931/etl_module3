"""Tests for Webinar 3: Temperature dataset transformation."""

import sys
import tempfile
from pathlib import Path

import pytest
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from webinar_3.transform_weather import transform_weather
from webinar_3.quality_checks import (
    validate_schema, validate_not_empty, remove_duplicates,
    remove_outliers_by_percentile,
)


@pytest.fixture
def tmp_output_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def sample_csv_path():
    return str(Path(__file__).resolve().parent.parent / "data" / "sample" / "sample_temperature.csv")


class TestQualityChecks:
    def test_validate_schema_passes(self):
        df = pd.DataFrame({"noted_date": ["01-01-2024"], "temp": [10.0], "out/in": ["in"]})
        result = validate_schema(df)
        assert len(result) == 1

    def test_validate_schema_fails(self):
        df = pd.DataFrame({"date": ["01-01-2024"], "temperature": [10.0]})
        with pytest.raises(ValueError, match="Missing required columns"):
            validate_schema(df)

    def test_validate_not_empty_passes(self):
        df = pd.DataFrame({"a": [1]})
        validate_not_empty(df)

    def test_validate_not_empty_fails(self):
        df = pd.DataFrame()
        with pytest.raises(ValueError, match="empty"):
            validate_not_empty(df)

    def test_remove_duplicates(self):
        df = pd.DataFrame({"a": [1, 1, 2], "b": [3, 3, 4]})
        result = remove_duplicates(df)
        assert len(result) == 2

    def test_remove_outliers(self):
        df = pd.DataFrame({"val": list(range(100))})
        result = remove_outliers_by_percentile(df, "val", 0.05, 0.95)
        assert result["val"].min() >= df["val"].quantile(0.05)
        assert result["val"].max() <= df["val"].quantile(0.95)


class TestTransformWeather:
    def test_full_transform(self, sample_csv_path, tmp_output_dir):
        result = transform_weather(sample_csv_path, tmp_output_dir)
        assert "cleaned" in result
        assert "hottest_5" in result
        assert "coldest_5" in result

    def test_hottest_5_has_five_rows(self, sample_csv_path, tmp_output_dir):
        result = transform_weather(sample_csv_path, tmp_output_dir)
        assert len(result["hottest_5"]) == 5

    def test_coldest_5_has_five_rows(self, sample_csv_path, tmp_output_dir):
        result = transform_weather(sample_csv_path, tmp_output_dir)
        assert len(result["coldest_5"]) == 5

    def test_only_indoor_readings(self, sample_csv_path, tmp_output_dir):
        result = transform_weather(sample_csv_path, tmp_output_dir)
        df = result["cleaned"]
        assert all(df["out/in"].str.lower() == "in")

    def test_date_format(self, sample_csv_path, tmp_output_dir):
        result = transform_weather(sample_csv_path, tmp_output_dir)
        df = result["cleaned"]
        assert pd.api.types.is_datetime64_any_dtype(df["noted_date"])

    def test_artifacts_saved(self, sample_csv_path, tmp_output_dir):
        transform_weather(sample_csv_path, tmp_output_dir)
        for fname in ["cleaned_weather.csv", "hottest_5_days.csv", "coldest_5_days.csv"]:
            assert (Path(tmp_output_dir) / fname).exists(), f"Missing artifact: {fname}"
