from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from db import build_database_url, get_missing_env_vars, normalize_database_url


class DbConfigTestCase(unittest.TestCase):
    def test_database_url_satisfies_required_config(self) -> None:
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pw@db.example.com:5432/postgres"}, clear=True):
            self.assertEqual(get_missing_env_vars(), [])
            self.assertEqual(
                build_database_url(),
                "postgresql+psycopg://user:pw@db.example.com:5432/postgres?sslmode=require",
            )

    def test_normalize_local_database_url_disables_ssl(self) -> None:
        self.assertEqual(
            normalize_database_url("postgresql://user:pw@localhost:5432/postgres"),
            "postgresql+psycopg://user:pw@localhost:5432/postgres?sslmode=disable",
        )

    def test_existing_sslmode_is_preserved(self) -> None:
        self.assertEqual(
            normalize_database_url("postgres://user:pw@db.example.com:5432/postgres?sslmode=require"),
            "postgresql+psycopg://user:pw@db.example.com:5432/postgres?sslmode=require",
        )


if __name__ == "__main__":
    unittest.main()
