
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError,
    VerificationError
)


load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured.")

password_hasher = PasswordHasher()


# 1. Hash password
def hash_password(password: str) -> str:

    if not password:
        raise ValueError("Password cannot be empty.")

    return password_hasher.hash(password)


# 2. Verify password
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    try:
        return password_hasher.verify(
            hashed_password,
            plain_password
        )

    except (VerifyMismatchError, VerificationError):
        return False


# 3. Generate JWT access token
def create_access_token(user_id: str) -> str:

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


# 4. Decode and validate JWT
def decode_access_token(token: str):

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]}
        )

        return payload["sub"]

    except jwt.InvalidTokenError:
        return None
