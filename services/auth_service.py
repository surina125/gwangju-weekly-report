from __future__ import annotations

import hashlib
import hmac
import os
import re
from base64 import b64decode, b64encode

from sqlalchemy import text

from db import get_engine


PBKDF2_ITERATIONS = 150_000
EMP_NO_PATTERN = re.compile(r"^[A-Za-z0-9]{7}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return "pbkdf2_sha256${iterations}${salt}${digest}".format(
        iterations=PBKDF2_ITERATIONS,
        salt=b64encode(salt).decode("ascii"),
        digest=b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt_b64, digest_b64 = stored_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    salt = b64decode(salt_b64.encode("ascii"))
    expected = b64decode(digest_b64.encode("ascii"))
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
    return hmac.compare_digest(actual, expected)


def normalize_emp_no(emp_no: str) -> str:
    return emp_no.strip().upper()


def username_from_emp_no(emp_no: str) -> str:
    return normalize_emp_no(emp_no).lower()


def validate_emp_no(emp_no: str) -> tuple[bool, str]:
    normalized = normalize_emp_no(emp_no)
    if not EMP_NO_PATTERN.fullmatch(normalized):
        return False, "직번은 숫자만 또는 영문/숫자 조합의 7자리여야 합니다."
    return True, normalized


def validate_email(email: str) -> tuple[bool, str]:
    normalized = email.strip().lower()
    if not EMAIL_PATTERN.fullmatch(normalized):
        return False, "이메일 형식이 올바르지 않습니다."
    return True, normalized


def ensure_auth_schema() -> None:
    ddl = """
    CREATE TABLE IF NOT EXISTS app_users (
        user_id SERIAL PRIMARY KEY,
        employee_id INTEGER NULL REFERENCES employees(employee_id),
        username VARCHAR(100) NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role VARCHAR(20) NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
    with get_engine().begin() as connection:
        connection.execute(text(ddl))


def ensure_admin_user() -> None:
    with get_engine().begin() as connection:
        admin_exists = connection.execute(
            text("SELECT 1 FROM app_users WHERE username = 'admin'")
        ).scalar_one_or_none()
        if admin_exists is None:
            connection.execute(
                text(
                    """
                    INSERT INTO app_users (employee_id, username, password_hash, role, is_active)
                    VALUES (NULL, 'admin', :password_hash, 'admin', TRUE)
                    """
                ),
                {"password_hash": hash_password("admin123!")},
            )


def cleanup_legacy_seeded_employee_users() -> None:
    with get_engine().begin() as connection:
        rows = connection.execute(
            text(
                """
                SELECT user_id, username, password_hash
                FROM app_users
                WHERE role = 'employee'
                """
            )
        ).mappings()

        removable_ids: list[int] = []
        for row in rows:
            username = str(row["username"]).lower()
            password_hash = str(row["password_hash"])
            if verify_password(username, password_hash):
                removable_ids.append(int(row["user_id"]))

        if removable_ids:
            connection.execute(
                text("DELETE FROM app_users WHERE user_id = ANY(:user_ids)"),
                {"user_ids": removable_ids},
            )


def register_user(
    emp_no: str,
    employee_name: str,
    department_id: int,
    cell_id: int,
    email: str,
    password: str,
) -> tuple[bool, str]:
    valid_emp_no, normalized_emp_no = validate_emp_no(emp_no)
    if not valid_emp_no:
        return False, normalized_emp_no

    valid_email, normalized_email = validate_email(email)
    if not valid_email:
        return False, normalized_email

    normalized_name = employee_name.strip()
    normalized_username = username_from_emp_no(normalized_emp_no)

    if len(password) < 8:
        return False, "비밀번호는 8자 이상이어야 합니다."

    with get_engine().begin() as connection:
        username_exists = connection.execute(
            text("SELECT 1 FROM app_users WHERE LOWER(username) = LOWER(:username)"),
            {"username": normalized_username},
        ).scalar_one_or_none()
        if username_exists is not None:
            return False, "이미 가입된 직번입니다. 로그인해 주세요."

        employee = connection.execute(
            text(
                """
                SELECT employee_id
                FROM employees
                WHERE UPPER(emp_no) = :emp_no
                """
            ),
            {
                "emp_no": normalized_emp_no,
            },
        ).scalar_one_or_none()

        if employee is None:
            employee = connection.execute(
                text("SELECT COALESCE(MAX(employee_id), 0) + 1 FROM employees")
            ).scalar_one()
            connection.execute(
                text(
                    """
                    INSERT INTO employees (
                        employee_id,
                        emp_no,
                        employee_name,
                        department_id,
                        cell_id,
                        email,
                        is_active
                    )
                    VALUES (
                        :employee_id,
                        :emp_no,
                        :employee_name,
                        :department_id,
                        :cell_id,
                        :email,
                        TRUE
                    )
                    """
                ),
                {
                    "employee_id": employee,
                    "emp_no": normalized_emp_no,
                    "employee_name": normalized_name,
                    "department_id": department_id,
                    "cell_id": cell_id,
                    "email": normalized_email,
                },
            )
        else:
            connection.execute(
                text(
                    """
                    UPDATE employees
                    SET employee_name = :employee_name,
                        department_id = :department_id,
                        cell_id = :cell_id,
                        email = :email,
                        is_active = TRUE
                    WHERE employee_id = :employee_id
                    """
                ),
                {
                    "employee_id": employee,
                    "employee_name": normalized_name,
                    "department_id": department_id,
                    "cell_id": cell_id,
                    "email": normalized_email,
                },
            )

        existing_account = connection.execute(
            text("SELECT 1 FROM app_users WHERE employee_id = :employee_id"),
            {"employee_id": employee},
        ).scalar_one_or_none()
        if existing_account is not None:
            return False, "이미 가입된 직원입니다. 로그인해 주세요."

        connection.execute(
            text(
                """
                INSERT INTO app_users (employee_id, username, password_hash, role, is_active)
                VALUES (:employee_id, :username, :password_hash, 'employee', TRUE)
                """
            ),
            {
                "employee_id": employee,
                "username": normalized_username,
                "password_hash": hash_password(password),
            },
        )

    return True, f"회원가입이 완료되었습니다. 로그인 아이디는 `{normalized_username}` 입니다."


def authenticate_user(username: str, password: str) -> dict[str, object] | None:
    query = """
        SELECT
            u.user_id,
            u.employee_id,
            u.username,
            u.password_hash,
            u.role,
            u.is_active,
            e.emp_no,
            e.employee_name,
            e.email,
            e.department_id,
            e.cell_id,
            d.department_name,
            c.cell_name
        FROM app_users u
        LEFT JOIN employees e ON e.employee_id = u.employee_id
        LEFT JOIN departments d ON d.department_id = e.department_id
        LEFT JOIN cells c ON c.cell_id = e.cell_id
        WHERE LOWER(u.username) = LOWER(:username)
    """
    with get_engine().connect() as connection:
        row = connection.execute(text(query), {"username": username.strip()}).mappings().first()

    if not row or not row["is_active"]:
        return None

    if not verify_password(password, str(row["password_hash"])):
        return None

    display_name = row["employee_name"] if row["employee_name"] else row["username"]
    return {
        "user_id": row["user_id"],
        "employee_id": row["employee_id"],
        "username": row["username"],
        "role": row["role"],
        "emp_no": row["emp_no"],
        "employee_name": row["employee_name"],
        "email": row["email"],
        "department_id": row["department_id"],
        "cell_id": row["cell_id"],
        "department_name": row["department_name"],
        "cell_name": row["cell_name"],
        "display_name": display_name,
    }
