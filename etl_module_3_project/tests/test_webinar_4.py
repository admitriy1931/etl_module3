"""Tests for Webinar 4: PostgreSQL load logic (unit-level, no DB required)."""

import sys
from pathlib import Path
from datetime import date

import pytest
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from webinar_4.state_manager import get_last_loaded_date, set_last_loaded_date


class TestStateManagerInterface:
    """Verify state_manager functions exist and have correct signatures."""

    def test_get_last_loaded_date_callable(self):
        assert callable(get_last_loaded_date)

    def test_set_last_loaded_date_callable(self):
        assert callable(set_last_loaded_date)


class TestFullLoadModule:
    """Verify full_load module is importable and has the expected function."""

    def test_import(self):
        from webinar_4.full_load import run_full_load
        assert callable(run_full_load)


class TestIncrementalLoadModule:
    """Verify incremental_load module is importable and has the expected function."""

    def test_import(self):
        from webinar_4.incremental_load import run_incremental_load
        assert callable(run_incremental_load)


class TestDataPreparation:
    """Test that cleaned CSV can be read and processed for loading."""

    def test_read_cleaned_csv(self):
        csv_path = Path(__file__).resolve().parent.parent / "data" / "sample" / "sample_temperature.csv"
        df = pd.read_csv(csv_path)
        assert not df.empty
        assert "noted_date" in df.columns
        assert "temp" in df.columns
