
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models import User
from backend.services.user_service import (
    create_user,
    get_user_by_email
)
from backend.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)


# 1. Register a new user
def register_user(
    db: Session,
    name: str,
    email: str,
    password: str
):
    name = name.strip()
    email = email.strip().lower()

    # Validate user details
    if not name:
        raise ValueError("Name cannot be empty.")

    if not email or "@" not in email:
        raise ValueError("Please enter a valid email address.")

    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    # Check whether email already exists
    existing_user = get_user_by_email(db, email)

    if existing_user is not None:
        raise ValueError("An account with this email already exists.")

    # Hash password before storing it
    password_hash = hash_password(password)

    try:
        new_user = create_user(
            db=db,
            name=name,
            email=email,
            password_hash=password_hash
        )

        return new_user

    except IntegrityError:
        db.rollback()
        raise ValueError("An account with this email already exists.")


# 2. Login an existing user
def login_user(
    db: Session,
    email: str,
    password: str
):
    email = email.strip().lower()

    # Find user by email
    user = get_user_by_email(db, email)

    if user is None:
        raise ValueError("Invalid email or password.")

    # Check whether account is active
    if not user.is_active:
        raise PermissionError("This account has been deactivated.")

    # Verify entered password against stored hash
    password_is_valid = verify_password(
        password,
        user.password_hash
    )

    if not password_is_valid:
        raise ValueError("Invalid email or password.")

    # Generate JWT after successful login
    access_token = create_access_token(str(user.id))

    return {
        "user": user,
        "access_token": access_token,
        "token_type": "bearer"
    }


# 3. Authenticate a user using JWT
def get_authenticated_user(
    db: Session,
    token: str
):
    # Decode and validate token
    user_id = decode_access_token(token)

    if user_id is None:
        return None

    # Convert token subject into UUID
    try:
        user_uuid = UUID(user_id)
    except (ValueError, TypeError):
        return None

    # Retrieve user from database
    user = db.get(User, user_uuid)

    if user is None or not user.is_active:
        return None

    return user
