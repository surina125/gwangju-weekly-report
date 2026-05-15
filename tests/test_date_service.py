from __future__ import annotations

import unittest
from datetime import date

from services.date_service import get_week_range


class DateServiceTestCase(unittest.TestCase):
    def test_week_range_from_wednesday(self) -> None:
        self.assertEqual(
            get_week_range(date(2026, 5, 13)),
            (date(2026, 5, 13), date(2026, 5, 19)),
        )

    def test_week_range_from_friday(self) -> None:
        self.assertEqual(
            get_week_range(date(2026, 5, 15)),
            (date(2026, 5, 13), date(2026, 5, 19)),
        )

    def test_week_range_from_tuesday(self) -> None:
        self.assertEqual(
            get_week_range(date(2026, 5, 19)),
            (date(2026, 5, 13), date(2026, 5, 19)),
        )

    def test_week_range_rolls_to_next_week(self) -> None:
        self.assertEqual(
            get_week_range(date(2026, 5, 20)),
            (date(2026, 5, 20), date(2026, 5, 26)),
        )


if __name__ == "__main__":
    unittest.main()
