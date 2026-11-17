
from sqlalchemy import create_engine, text
from backend.config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD
)

DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            print("Database connected successfully!")
            print(result.scalar())

    except Exception as e:
        print("Database connection failed!")
        print(e)
