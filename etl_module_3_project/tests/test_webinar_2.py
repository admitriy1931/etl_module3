"""Tests for Webinar 2: JSON and XML flattening."""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from webinar_2.flatten_json import flatten_json
from webinar_2.flatten_xml import flatten_xml


@pytest.fixture
def tmp_output_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def sample_json_path():
    return str(Path(__file__).resolve().parent.parent / "data" / "sample" / "sample_nested.json")


@pytest.fixture
def sample_xml_path():
    return str(Path(__file__).resolve().parent.parent / "data" / "sample" / "sample_nested.xml")


class TestFlattenJSON:
    def test_produces_all_tables(self, sample_json_path, tmp_output_dir):
        result = flatten_json(sample_json_path, tmp_output_dir)
        assert "employees" in result
        assert "employee_skills" in result
        assert "employee_projects" in result
        assert "offices" in result

    def test_employees_not_empty(self, sample_json_path, tmp_output_dir):
        result = flatten_json(sample_json_path, tmp_output_dir)
        assert len(result["employees"]) > 0

    def test_employees_have_required_columns(self, sample_json_path, tmp_output_dir):
        result = flatten_json(sample_json_path, tmp_output_dir)
        df = result["employees"]
        for col in ["company", "department_name", "employee_id", "employee_first_name", "employee_role"]:
            assert col in df.columns, f"Missing column: {col}"

    def test_csv_files_created(self, sample_json_path, tmp_output_dir):
        flatten_json(sample_json_path, tmp_output_dir)
        expected_files = [
            "json_employees.csv",
            "json_employee_skills.csv",
            "json_employee_projects.csv",
            "json_offices.csv",
        ]
        for f in expected_files:
            assert (Path(tmp_output_dir) / f).exists(), f"File not created: {f}"

    def test_skills_linked_to_employees(self, sample_json_path, tmp_output_dir):
        result = flatten_json(sample_json_path, tmp_output_dir)
        emp_ids = set(result["employees"]["employee_id"])
        skill_emp_ids = set(result["employee_skills"]["employee_id"])
        assert skill_emp_ids.issubset(emp_ids)


class TestFlattenXML:
    def test_produces_all_tables(self, sample_xml_path, tmp_output_dir):
        result = flatten_xml(sample_xml_path, tmp_output_dir)
        assert "books" in result
        assert "book_tags" in result
        assert "book_reviews" in result

    def test_books_not_empty(self, sample_xml_path, tmp_output_dir):
        result = flatten_xml(sample_xml_path, tmp_output_dir)
        assert len(result["books"]) > 0

    def test_books_have_required_columns(self, sample_xml_path, tmp_output_dir):
        result = flatten_xml(sample_xml_path, tmp_output_dir)
        df = result["books"]
        for col in ["store_name", "book_id", "title", "author_first_name", "price"]:
            assert col in df.columns, f"Missing column: {col}"

    def test_csv_files_created(self, sample_xml_path, tmp_output_dir):
        flatten_xml(sample_xml_path, tmp_output_dir)
        expected_files = [
            "xml_books.csv",
            "xml_book_tags.csv",
            "xml_book_reviews.csv",
        ]
        for f in expected_files:
            assert (Path(tmp_output_dir) / f).exists(), f"File not created: {f}"
