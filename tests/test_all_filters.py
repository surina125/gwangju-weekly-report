from __future__ import annotations

import unittest
from datetime import date

from services.employee_service import get_cells_by_department, get_employees
from services.report_service import (
    get_not_submitted_employees,
    get_progress_chart_data,
    get_report_summary_metrics,
    get_reports_by_cell,
    get_submission_chart_data,
    get_weekly_trend_chart_data,
)


class AllFilterTestCase(unittest.TestCase):
    def test_get_cells_with_all_filter(self) -> None:
        result = get_cells_by_department(None)
        self.assertGreaterEqual(len(result), 8)

    def test_get_employees_with_all_filter(self) -> None:
        result = get_employees(None, None)
        self.assertGreaterEqual(len(result), 18)

    def test_get_reports_with_all_filter(self) -> None:
        result = get_reports_by_cell(date(2026, 5, 13), date(2026, 5, 19), None, None)
        self.assertGreaterEqual(len(result), 1)
        self.assertIn("부서", result.columns)
        self.assertIn("셀", result.columns)

    def test_get_not_submitted_with_all_filter(self) -> None:
        result = get_not_submitted_employees(date(2026, 5, 13), date(2026, 5, 19), None, None)
        self.assertGreaterEqual(len(result), 1)
        self.assertIn("부서", result.columns)
        self.assertIn("셀", result.columns)

    def test_chart_analysis_queries(self) -> None:
        summary = get_report_summary_metrics(date(2026, 5, 13), date(2026, 5, 19), None, None)
        self.assertGreaterEqual(summary["total_employees"], 1)

        submissions = get_submission_chart_data(date(2026, 5, 13), date(2026, 5, 19), None)
        self.assertIn("셀", submissions.columns)
        self.assertIn("제출", submissions.columns)

        progress = get_progress_chart_data(date(2026, 5, 13), date(2026, 5, 19), None, None)
        self.assertIn("셀", progress.columns)
        self.assertIn("평균 진행률", progress.columns)

        trend = get_weekly_trend_chart_data()
        self.assertIn("week_label", trend.columns)


if __name__ == "__main__":
    unittest.main()
