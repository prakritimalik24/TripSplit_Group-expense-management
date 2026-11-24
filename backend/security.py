
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError
)


load_dotenv()


# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
except ValueError:
    raise RuntimeError(
        "ACCESS_TOKEN_EXPIRE_MINUTES must be a valid integer."
    )


if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured.")

if len(JWT_SECRET_KEY.encode("utf-8")) < 32:
    raise RuntimeError(
        "JWT_SECRET_KEY must contain at least 32 bytes."
    )

# This application currently uses symmetric HS256 signing.
if JWT_ALGORITHM != "HS256":
    raise RuntimeError("Only HS256 JWT algorithm is supported.")

if ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
    raise RuntimeError(
        "ACCESS_TOKEN_EXPIRE_MINUTES must be positive."
    )


password_hasher = PasswordHasher()


# 1. Hash password
def hash_password(password: str) -> str:

    if not isinstance(password, str) or not password:
        raise ValueError("Password cannot be empty.")

    return password_hasher.hash(password)


# 2. Verify password
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    if not isinstance(plain_password, str):
        return False

    if not isinstance(hashed_password, str) or not hashed_password:
        return False

    try:
        return password_hasher.verify(
            hashed_password,
            plain_password
        )

    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError,
        TypeError,
        ValueError
    ):
        return False


# 3. Generate JWT access token
def create_access_token(user_id: str) -> str:

    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("A valid user ID is required.")

    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "iat": now,
        "exp": expires_at
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


# 4. Decode and validate JWT
def decode_access_token(token: str) -> str | None:

    if not isinstance(token, str) or not token:
        return None

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={
                "require": ["sub", "iat", "exp"],
                "verify_signature": True,
                "verify_exp": True
            }
        )

        user_id = payload.get("sub")

        if not isinstance(user_id, str) or not user_id.strip():
            return None

        return user_id

    except (
        jwt.InvalidTokenError,
        TypeError,
        ValueError
    ):
        return None
