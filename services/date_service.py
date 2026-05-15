from __future__ import annotations

import os
from datetime import date, timedelta


DAY_NAME_TO_INDEX = {
    "MONDAY": 0,
    "TUESDAY": 1,
    "WEDNESDAY": 2,
    "THURSDAY": 3,
    "FRIDAY": 4,
    "SATURDAY": 5,
    "SUNDAY": 6,
}


def resolve_week_start_day(value: str | None = None) -> int:
    raw_value = (value or os.getenv("REPORT_WEEK_START_DAY") or "WEDNESDAY").strip().upper()

    if raw_value.isdigit():
        day_index = int(raw_value)
        if 0 <= day_index <= 6:
            return day_index
        raise ValueError("REPORT_WEEK_START_DAY numeric value must be between 0 and 6.")

    if raw_value not in DAY_NAME_TO_INDEX:
        raise ValueError(f"Unsupported REPORT_WEEK_START_DAY value: {raw_value}")

    return DAY_NAME_TO_INDEX[raw_value]


def get_week_range(base_date: date, week_start_day: int | None = None) -> tuple[date, date]:
    start_day = resolve_week_start_day() if week_start_day is None else week_start_day
    delta = (base_date.weekday() - start_day) % 7
    week_start = base_date - timedelta(days=delta)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def format_week_label(week_start: date, week_end: date) -> str:
    return f"{week_start.isoformat()} ~ {week_end.isoformat()}"
