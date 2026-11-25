
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from backend.config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    DB_SSLMODE
)


DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)

connect_args = {}

if DB_SSLMODE:
    connect_args["sslmode"] = DB_SSLMODE

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args
)


def test_connection():

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT version()")
            )

            print("Database connected successfully!")
            print(result.scalar())

    except Exception:
        print("Database connection failed!")
        raise
