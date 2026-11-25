
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_config_value(key, default=None):
    """
    Read configuration from environment variables first,
    then fall back to Streamlit Secrets.
    """

    value = os.getenv(key)

    if value is not None and value.strip():
        return value

    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


DB_HOST = get_config_value("DB_HOST")
DB_PORT = get_config_value("DB_PORT", "5432")
DB_NAME = get_config_value("DB_NAME")
DB_USER = get_config_value("DB_USER")
DB_PASSWORD = get_config_value("DB_PASSWORD")

DB_SSLMODE = get_config_value("DB_SSLMODE")


# Validate required database configuration.
required_settings = {
    "DB_HOST": DB_HOST,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD
}

missing_settings = [
    key
    for key, value in required_settings.items()
    if not value
]

if missing_settings:
    raise RuntimeError(
        f"Missing database configuration: "
        f"{', '.join(missing_settings)}"
    )

DB_PORT = int(DB_PORT)
