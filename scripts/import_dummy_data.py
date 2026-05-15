from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from db import get_engine


WORKBOOK_PATH = BASE_DIR / "weekly_report_dummy_db_data_cell_notification.xlsx"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"

SHEET_TABLE_MAP = {
    "departments": "departments",
    "cells": "cells",
    "employees": "employees",
    "weekly_reports": "weekly_reports",
    "weekly_report_items": "weekly_report_items",
    "weekly_notifications": "weekly_notifications",
}

DATE_COLUMNS = {
    "weekly_reports": ["week_start", "week_end", "submitted_at", "reminder_sent_at"],
    "weekly_notifications": ["week_start", "week_end", "checked_at"],
}


def normalize_frame(table_name: str, frame: pd.DataFrame) -> pd.DataFrame:
    cleaned = frame.copy()
    cleaned.columns = [str(column).strip() for column in cleaned.columns]
    cleaned = cleaned.where(pd.notna(cleaned), None)

    if table_name == "employees":
        cleaned["is_active"] = cleaned["is_active"].map({"Y": True, "N": False}).fillna(False)

    for column in DATE_COLUMNS.get(table_name, []):
        if column in cleaned.columns:
            cleaned[column] = pd.to_datetime(cleaned[column], errors="coerce")

    if table_name == "weekly_notifications" and "sent_yn" in cleaned.columns:
        cleaned["sent_yn"] = cleaned["sent_yn"].fillna("N")

    return cleaned


def apply_schema() -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_engine().begin() as connection:
        for statement in [part.strip() for part in sql.split(";") if part.strip()]:
            connection.exec_driver_sql(statement)


def import_workbook() -> None:
    workbook = pd.ExcelFile(WORKBOOK_PATH)

    with get_engine().begin() as connection:
        for table_name in reversed(list(SHEET_TABLE_MAP.values())):
            connection.exec_driver_sql(f"DELETE FROM {table_name}")

        for sheet_name, table_name in SHEET_TABLE_MAP.items():
            frame = pd.read_excel(workbook, sheet_name=sheet_name)
            normalized = normalize_frame(table_name, frame)
            normalized.to_sql(table_name, connection, if_exists="append", index=False)
            print(f"Imported {sheet_name} -> {table_name}: {len(normalized)} rows")


if __name__ == "__main__":
    apply_schema()
    import_workbook()
    print("Schema applied and dummy data imported successfully.")
