from __future__ import annotations

import unittest
from datetime import date

from app import build_download_filename
from db import read_sql
from services.report_service import create_not_submitted_notifications, get_not_submitted_employees, save_weekly_report


class PrdRequirementTestCase(unittest.TestCase):
    def test_download_filename_includes_department_and_cell(self) -> None:
        filename = build_download_filename(
            prefix="주간업무보고",
            extension="xlsx",
            department_name="IT개발부",
            cell_name="여신",
            selected_period=(date(2026, 5, 13), date(2026, 5, 19)),
        )
        self.assertEqual(filename, "IT개발부_여신_주간업무보고_20260513_20260519.xlsx")

    def test_not_submitted_rows_have_miwijak_status(self) -> None:
        result = get_not_submitted_employees(
            week_start=date(2026, 5, 13),
            week_end=date(2026, 5, 19),
            department_id=3,
            cell_id=7,
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["작성상태"], "미작성")

    def test_save_weekly_report_rejects_invalid_progress(self) -> None:
        with self.assertRaises(ValueError):
            save_weekly_report(
                employee_id=1,
                week_start=date(2026, 5, 13),
                week_end=date(2026, 5, 19),
                items=[
                    {
                        "sr_title": "잘못된 진행률",
                        "progress": 101,
                        "sr_dev_content": "실패해야 함",
                    }
                ],
            )

    def test_tuesday_notification_targets_are_saved(self) -> None:
        created = create_not_submitted_notifications(
            week_start=date(2026, 5, 13),
            week_end=date(2026, 5, 19),
            department_id=3,
            cell_id=7,
        )
        self.assertEqual(created, 1)

        rows = read_sql(
            """
            SELECT notification_type, target_status, sent_yn
            FROM weekly_notifications wn
            JOIN employees e ON e.employee_id = wn.employee_id
            WHERE wn.week_start = '2026-05-13'
              AND wn.week_end = '2026-05-19'
              AND e.emp_no = 'Q12R769'
              AND wn.notification_type = 'NOT_SUBMITTED'
            """
        )
        self.assertFalse(rows.empty)
        self.assertEqual(rows.iloc[0]["notification_type"], "NOT_SUBMITTED")
        self.assertEqual(rows.iloc[0]["target_status"], "미작성")
        self.assertEqual(rows.iloc[0]["sent_yn"], "N")


if __name__ == "__main__":
    unittest.main()
