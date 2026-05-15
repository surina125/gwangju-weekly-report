from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

REQUIRED_DB_ENV_VARS = [
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
]


class MissingEnvironmentError(RuntimeError):
    """Raised when a required environment value is missing."""


def _load_streamlit_secrets_into_env() -> None:
    """Allow Streamlit Community Cloud secrets to satisfy env-based config."""
    try:
        secrets = st.secrets
    except Exception:
        return

    for key in REQUIRED_DB_ENV_VARS + ["DB_SSLMODE"]:
        value = secrets.get(key)
        if value is not None and not os.getenv(key):
            os.environ[key] = str(value)


def get_missing_env_vars() -> list[str]:
    _load_streamlit_secrets_into_env()
    return [key for key in REQUIRED_DB_ENV_VARS if not os.getenv(key)]


def validate_db_env() -> None:
    missing = get_missing_env_vars()
    if missing:
        joined = ", ".join(missing)
        raise MissingEnvironmentError(f"Missing required environment variables: {joined}")


def build_database_url() -> str:
    validate_db_env()

    host = os.environ["DB_HOST"]
    port = os.environ["DB_PORT"]
    db_name = os.environ["DB_NAME"]
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    sslmode = os.getenv("DB_SSLMODE")
    if not sslmode:
        normalized_host = host.strip().lower()
        sslmode = "disable" if normalized_host in {"localhost", "127.0.0.1", "::1"} else "require"

    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}?sslmode={sslmode}"


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(build_database_url(), pool_pre_ping=True)


def healthcheck() -> None:
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))


def read_sql(query: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
    with get_engine().connect() as connection:
        return pd.read_sql(text(query), connection, params=params or {})


def execute_sql(query: str, params: dict[str, Any] | None = None) -> None:
    with get_engine().begin() as connection:
        connection.execute(text(query), params or {})
