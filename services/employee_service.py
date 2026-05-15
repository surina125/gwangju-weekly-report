from __future__ import annotations

import pandas as pd

from db import read_sql


def get_departments() -> pd.DataFrame:
    query = """
        SELECT department_id, department_name, description
        FROM departments
        ORDER BY department_id
    """
    return read_sql(query)


def get_cells_by_department(department_id: int | None = None) -> pd.DataFrame:
    query = """
        SELECT cell_id, department_id, cell_name, description
        FROM cells
    """
    params: dict[str, object] = {}

    if department_id is not None:
        query += "\nWHERE department_id = :department_id"
        params["department_id"] = department_id

    query += "\nORDER BY department_id, cell_id"
    return read_sql(query, params)


def get_employees(department_id: int | None = None, cell_id: int | None = None) -> pd.DataFrame:
    query = """
        SELECT
            e.employee_id,
            e.emp_no AS "직번",
            e.employee_name AS "이름",
            d.department_name AS "부서",
            c.cell_name AS "셀",
            e.email AS "이메일",
            CASE WHEN e.is_active THEN 'Y' ELSE 'N' END AS "재직여부"
        FROM employees e
        JOIN departments d ON d.department_id = e.department_id
        JOIN cells c ON c.cell_id = e.cell_id
    """
    conditions: list[str] = []
    params: dict[str, object] = {}

    if department_id is not None:
        conditions.append("e.department_id = :department_id")
        params["department_id"] = department_id

    if cell_id is not None:
        conditions.append("e.cell_id = :cell_id")
        params["cell_id"] = cell_id

    if conditions:
        query += "\nWHERE " + " AND ".join(conditions)

    query += "\nORDER BY e.employee_id"
    return read_sql(query, params)
