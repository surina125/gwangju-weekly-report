from __future__ import annotations

import unittest
from datetime import date

from services.report_service import get_reports_by_cell, save_weekly_report


class ReportWriteFlowTestCase(unittest.TestCase):
    def test_save_weekly_report_updates_existing_period_report(self) -> None:
        report_id = save_weekly_report(
            employee_id=4,
            week_start=date(2026, 5, 13),
            week_end=date(2026, 5, 19),
            items=[
                {
                    "sr_title": "테스트 입력 저장 확인",
                    "progress": 55,
                    "sr_dev_content": "저장 후 조회와 DB 반영 여부 검증",
                }
            ],
        )
        self.assertIsInstance(report_id, int)

        reports = get_reports_by_cell(
            week_start=date(2026, 5, 13),
            week_end=date(2026, 5, 19),
            department_id=1,
            cell_id=2,
        )
        subset = reports[reports["직번"] == "D50E116"]
        self.assertFalse(subset.empty)
        self.assertIn("테스트 입력 저장 확인", subset["SR 제목"].tolist())


if __name__ == "__main__":
    unittest.main()
