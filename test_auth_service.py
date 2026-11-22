
from uuid import uuid4

from backend.db.session import SessionLocal
from backend.services.auth_service import (
    register_user,
    login_user,
    get_authenticated_user
)


def expect_error(function, error_type):
    try:
        function()
    except error_type:
        return
    else:
        raise AssertionError(
            f"Expected {error_type.__name__} was not raised."
        )


db = SessionLocal()

try:
    email = f"auth_{uuid4().hex[:8]}@example.com"
    password = "TripSplit@123"

    # 1. Test user registration
    user = register_user(
        db,
        name="Test User",
        email=email.upper(),
        password=password
    )

    assert user is not None
    assert user.email == email
    assert user.name == "Test User"

    print("PASS: User registration")

    # 2. Verify password is hashed
    assert user.password_hash != password

    print("PASS: Password is stored as a hash")

    # 3. Test duplicate email registration
    expect_error(
        lambda: register_user(
            db,
            name="Another User",
            email=email,
            password=password
        ),
        ValueError
    )

    print("PASS: Duplicate email rejection")

    # 4. Test invalid registration details
    expect_error(
        lambda: register_user(
            db,
            name="",
            email=f"empty_{uuid4().hex[:8]}@example.com",
            password=password
        ),
        ValueError
    )

    expect_error(
        lambda: register_user(
            db,
            name="Short Password",
            email=f"short_{uuid4().hex[:8]}@example.com",
            password="123"
        ),
        ValueError
    )

    print("PASS: Registration validation")

    # 5. Test successful login
    login_result = login_user(
        db,
        email=email,
        password=password
    )

    assert login_result["user"].id == user.id
    assert login_result["access_token"]
    assert login_result["token_type"] == "bearer"

    print("PASS: Successful login")

    # 6. Test incorrect password
    expect_error(
        lambda: login_user(
            db,
            email=email,
            password="WrongPassword123"
        ),
        ValueError
    )

    print("PASS: Incorrect password rejection")

    # 7. Test authenticated user using JWT
    token = login_result["access_token"]

    authenticated_user = get_authenticated_user(
        db,
        token
    )

    assert authenticated_user is not None
    assert authenticated_user.id == user.id

    print("PASS: JWT authentication")

    # 8. Test invalid JWT
    invalid_user = get_authenticated_user(
        db,
        "invalid-token"
    )

    assert invalid_user is None

    print("PASS: Invalid JWT rejection")

    # 9. Test deactivated account
    user.is_active = False
    db.commit()

    expect_error(
        lambda: login_user(
            db,
            email=email,
            password=password
        ),
        PermissionError
    )

    assert get_authenticated_user(db, token) is None

    print("PASS: Deactivated account rejection")

    print("\nAll authentication tests passed!")

finally:
    db.close()
