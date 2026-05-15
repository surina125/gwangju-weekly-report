from __future__ import annotations

import unittest
from datetime import date

from services.report_service import get_reports_by_cell
from services.word_service import build_report_docx


class WordServiceTestCase(unittest.TestCase):
    def test_build_report_docx_returns_docx_bytes(self) -> None:
        dataframe = get_reports_by_cell(date(2026, 5, 13), date(2026, 5, 19), department_id=1, cell_id=1)
        result = build_report_docx(
            dataframe=dataframe,
            week_start=date(2026, 5, 13),
            week_end=date(2026, 5, 19),
            department_name="IT개발부",
            cell_name="여신",
        )
        self.assertGreater(len(result), 1000)
        self.assertEqual(result[:2], b"PK")


if __name__ == "__main__":
    unittest.main()
