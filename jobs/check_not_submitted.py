from __future__ import annotations

from datetime import date

from services.date_service import get_week_range
from services.report_service import create_not_submitted_notifications, get_not_submitted_employees


def main() -> None:
    week_start, week_end = get_week_range(date.today())
    created = create_not_submitted_notifications(week_start=week_start, week_end=week_end)
    targets = get_not_submitted_employees(week_start=week_start, week_end=week_end)

    print(f"week_start={week_start} week_end={week_end}")
    print(f"created_notifications={created}")
    print(targets.to_string(index=False))


if __name__ == "__main__":
    main()
