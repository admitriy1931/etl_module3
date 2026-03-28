"""Flatten nested JSON into tabular structures."""

from pathlib import Path
from typing import Dict, List

import pandas as pd

from utils.logger import get_logger
from utils.io_helpers import read_json_file, save_dataframe
from webinar_2.schemas import (
    EMPLOYEE_COLUMNS, EMPLOYEE_SKILL_COLUMNS,
    EMPLOYEE_PROJECT_COLUMNS, OFFICE_COLUMNS,
)

log = get_logger(__name__)


def flatten_json(input_path: str, output_dir: str) -> Dict[str, pd.DataFrame]:
    """Read nested JSON and produce flat DataFrames for each entity."""
    data = read_json_file(input_path)
    company_name = data.get("company", "Unknown")

    employees_rows: List[dict] = []
    skills_rows: List[dict] = []
    projects_rows: List[dict] = []
    offices_rows: List[dict] = []

    for dept in data.get("departments", []):
        dept_name = dept.get("name", "")
        head = dept.get("head", {})
        head_contact = head.get("contact", {})

        for emp in dept.get("employees", []):
            emp_id = emp.get("id")
            employees_rows.append({
                "company": company_name,
                "department_name": dept_name,
                "dept_head_first_name": head.get("first_name", ""),
                "dept_head_last_name": head.get("last_name", ""),
                "dept_head_email": head_contact.get("email", ""),
                "dept_head_phone": head_contact.get("phone", ""),
                "employee_id": emp_id,
                "employee_first_name": emp.get("first_name", ""),
                "employee_last_name": emp.get("last_name", ""),
                "employee_role": emp.get("role", ""),
            })

            for skill in emp.get("skills", []):
                skills_rows.append({
                    "employee_id": emp_id,
                    "skill": skill,
                })

            for proj in emp.get("projects", []):
                projects_rows.append({
                    "employee_id": emp_id,
                    "project_id": proj.get("project_id", ""),
                    "project_name": proj.get("name", ""),
                    "project_status": proj.get("status", ""),
                })

    for office in data.get("offices", []):
        offices_rows.append({
            "company": company_name,
            "city": office.get("city", ""),
            "address": office.get("address", ""),
            "capacity": office.get("capacity", 0),
        })

    result = {}

    df_employees = pd.DataFrame(employees_rows, columns=EMPLOYEE_COLUMNS)
    result["employees"] = df_employees
    save_dataframe(df_employees, str(Path(output_dir) / "json_employees.csv"))
    log.info("Flattened %d employees", len(df_employees))

    df_skills = pd.DataFrame(skills_rows, columns=EMPLOYEE_SKILL_COLUMNS)
    result["employee_skills"] = df_skills
    save_dataframe(df_skills, str(Path(output_dir) / "json_employee_skills.csv"))
    log.info("Flattened %d employee-skill pairs", len(df_skills))

    df_projects = pd.DataFrame(projects_rows, columns=EMPLOYEE_PROJECT_COLUMNS)
    result["employee_projects"] = df_projects
    save_dataframe(df_projects, str(Path(output_dir) / "json_employee_projects.csv"))
    log.info("Flattened %d employee-project pairs", len(df_projects))

    df_offices = pd.DataFrame(offices_rows, columns=OFFICE_COLUMNS)
    result["offices"] = df_offices
    save_dataframe(df_offices, str(Path(output_dir) / "json_offices.csv"))
    log.info("Flattened %d offices", len(df_offices))

    return result
