
import uuid

from backend.db.session import SessionLocal
from backend.services.user_service import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user,
    deactivate_user
)

db = SessionLocal()

try:
    # 1. Create a user
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    user = create_user(
        db,
        name="Test User",
        email=unique_email,
        password_hash="test_hash_not_a_real_password"
    )

    print("Created:", user.name, user.email)

    # 2. Get user by email
    found_user = get_user_by_email(db, unique_email)
    print("Found by email:", found_user.name)

    # 3. Get user by ID
    found_user = get_user_by_id(db, user.id)
    print("Found by ID:", found_user.name)

    # 4. Update user
    updated_user = update_user(
        db,
        user.id,
        name="Updated Test User"
    )
    print("Updated name:", updated_user.name)

    # 5. Deactivate user
    deactivated_user = deactivate_user(db, user.id)
    print("Active status:", deactivated_user.is_active)

finally:
    db.close()
