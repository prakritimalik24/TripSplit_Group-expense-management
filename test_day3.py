
from datetime import date
from uuid import uuid4

from backend.db.session import SessionLocal
from backend.services.user_service import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user,
    deactivate_user
)
from backend.services.group_service import (
    create_group,
    get_group_by_id,
    get_all_groups,
    update_group,
    delete_group
)


db = SessionLocal()

try:
    # USER CRUD

    email = f"day3_{uuid4().hex[:8]}@example.com"

    user = create_user(
        db,
        name="Day 3 Test User",
        email=email,
        password_hash="test_hash"
    )
    assert user.name == "Day 3 Test User"
    print("PASS: Create user")

    found_email = get_user_by_email(db, email)
    assert found_email is not None
    print("PASS: Get user by email")

    found_id = get_user_by_id(db, user.id)
    assert found_id is not None
    print("PASS: Get user by ID")

    updated_user = update_user(
        db, user.id, name="Updated Day 3 User"
    )
    assert updated_user.name == "Updated Day 3 User"
    print("PASS: Update user")

    # GROUP CRUD

    group = create_group(
        db,
        name="Day 3 Trip",
        created_by=user.id,
        description="Verification group",
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 15)
    )
    assert group.id is not None
    print("PASS: Create group")

    found_group = get_group_by_id(db, group.id, user.id)
    assert found_group is not None
    print("PASS: Get group by ID")

    groups = get_all_groups(db, user.id)
    assert any(g.id == group.id for g in groups)
    print("PASS: Get all groups")

    updated_group = update_group(
        db, group.id, user.id, name="Updated Day 3 Trip"
    )
    assert updated_group.name == "Updated Day 3 Trip"
    print("PASS: Update group")

    archived_group = delete_group(db, group.id, user.id)
    assert archived_group.status == "archived"
    print("PASS: Archive group")

    # USER DEACTIVATION

    deactivated_user = deactivate_user(db, user.id)
    assert deactivated_user.is_active is False
    print("PASS: Deactivate user")

    print("\nAll Day 3 verification checks passed!")

finally:
    db.close()
