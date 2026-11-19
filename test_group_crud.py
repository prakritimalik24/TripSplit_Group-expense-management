
from datetime import date
from uuid import uuid4

from backend.db.session import SessionLocal
from backend.services.user_service import create_user
from backend.services.group_service import (
    create_group,
    get_group_by_id,
    get_all_groups,
    update_group,
    delete_group
)

db = SessionLocal()

try:
    # 1. Create a test user
    email = f"group_test_{uuid4().hex[:8]}@example.com"

    user = create_user(
        db,
        name="Group Test User",
        email=email,
        password_hash="test_hash"
    )

    print("User created:", user.name)

    # 2. Create a group
    group = create_group(
        db,
        name="Goa Trip",
        created_by=user.id,
        description="College friends trip",
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 15)
    )

    print("Group created:", group.name)
    print("Group ID:", group.id)

    # 3. Get group by ID
    found_group = get_group_by_id(
        db,
        group.id,
        user.id
    )

    print("Found group:", found_group.name)

    # 4. Get all groups for user
    groups = get_all_groups(db, user.id)

    print("Total groups:", len(groups))

    # 5. Update group
    updated_group = update_group(
        db,
        group.id,
        user.id,
        name="Goa Vacation"
    )

    print("Updated group:", updated_group.name)

    # 6. Archive group
    archived_group = delete_group(
        db,
        group.id,
        user.id
    )

    print("Group status:", archived_group.status)

finally:
    db.close()
