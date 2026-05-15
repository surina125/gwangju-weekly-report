from __future__ import annotations

import unittest

from db import get_engine
from services.auth_service import (
    authenticate_user,
    cleanup_legacy_seeded_employee_users,
    ensure_admin_user,
    ensure_auth_schema,
    hash_password,
    register_user,
    username_from_emp_no,
    validate_emp_no,
    verify_password,
)


class AuthServiceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ensure_auth_schema()
        ensure_admin_user()
        cleanup_legacy_seeded_employee_users()

    def test_hash_and_verify_password(self) -> None:
        hashed = hash_password("secret123")
        self.assertTrue(verify_password("secret123", hashed))
        self.assertFalse(verify_password("wrong", hashed))

    def test_emp_no_validation_and_username_generation(self) -> None:
        valid, normalized = validate_emp_no("a24b901")
        self.assertTrue(valid)
        self.assertEqual(normalized, "A24B901")
        self.assertEqual(username_from_emp_no("a24b901"), "a24b901")

        numeric_valid, numeric_normalized = validate_emp_no("1234567")
        self.assertTrue(numeric_valid)
        self.assertEqual(numeric_normalized, "1234567")

        invalid, message = validate_emp_no("ABC123")
        self.assertFalse(invalid)
        self.assertEqual(message, "직번은 숫자만 또는 영문/숫자 조합의 7자리여야 합니다.")

    def test_admin_authentication(self) -> None:
        user = authenticate_user("admin", "admin123!")
        self.assertIsNotNone(user)
        assert user is not None
        self.assertEqual(user["role"], "admin")

    def test_register_and_authenticate_employee(self) -> None:
        with get_engine().begin() as connection:
            connection.exec_driver_sql("DELETE FROM app_users WHERE username = 'z99z999'")
            connection.exec_driver_sql("DELETE FROM employees WHERE emp_no = 'Z99Z999'")

        success, message = register_user(
            emp_no="Z99Z999",
            employee_name="테스트직원",
            department_id=1,
            cell_id=1,
            email="test.employee@example.com",
            password="pw123456",
        )
        self.assertTrue(success, message)
        self.assertIn("z99z999", message)

        user = authenticate_user("z99z999", "pw123456")
        self.assertIsNotNone(user)
        assert user is not None
        self.assertEqual(user["role"], "employee")
        self.assertEqual(user["emp_no"], "Z99Z999")
        self.assertEqual(user["employee_name"], "테스트직원")
        self.assertEqual(user["department_id"], 1)
        self.assertEqual(user["cell_id"], 1)


if __name__ == "__main__":
    unittest.main()
