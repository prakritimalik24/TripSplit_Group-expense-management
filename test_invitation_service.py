
import hashlib

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select

from backend.db.session import SessionLocal
from backend.models import GroupMember, Invitation

from backend.services.user_service import create_user
from backend.services.group_service import create_group

from backend.services.invitation_service import (
    create_invitation,
    accept_invitation
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


def hash_token(token):
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


db = SessionLocal()

try:
    # 1. Create test users
    admin = create_user(
        db,
        name="Admin User",
        email=f"admin_{uuid4().hex[:8]}@example.com",
        password_hash="test_hash"
    )

    member = create_user(
        db,
        name="Member User",
        email=f"member_{uuid4().hex[:8]}@example.com",
        password_hash="test_hash"
    )

    another_member = create_user(
        db,
        name="Another User",
        email=f"another_{uuid4().hex[:8]}@example.com",
        password_hash="test_hash"
    )

    print("PASS: Test users created")

    # 2. Create group
    group = create_group(
        db,
        name="Invitation Test Group",
        created_by=admin.id
    )

    print("PASS: Test group created")

    # 3. Add an ordinary member
    ordinary_membership = GroupMember(
        group_id=group.id,
        user_id=another_member.id,
        role="member"
    )

    db.add(ordinary_membership)
    db.commit()

    print("PASS: Ordinary group member added")

    # 4. Test non-admin invitation rejection
    expect_error(
        lambda: create_invitation(
            db,
            group_id=group.id,
            invited_by=another_member.id
        ),
        PermissionError
    )

    print("PASS: Non-admin invitation rejection")

    # 5. Test admin invitation creation
    invitation_result = create_invitation(
        db,
        group_id=group.id,
        invited_by=admin.id
    )

    assert invitation_result["token"]
    assert invitation_result["group_id"] == group.id

    print("PASS: Admin invitation creation")

    # 6. Verify only token hash is stored
    stored_invitation = db.get(
        Invitation,
        invitation_result["invitation_id"]
    )

    assert stored_invitation.token_hash != invitation_result["token"]

    assert stored_invitation.token_hash == hash_token(
        invitation_result["token"]
    )

    print("PASS: Invitation token hashing")

    # 7. Test successful invitation acceptance
    membership = accept_invitation(
        db,
        token=invitation_result["token"],
        user_id=member.id
    )

    assert membership.group_id == group.id
    assert membership.user_id == member.id
    assert membership.role == "member"

    print("PASS: Invitation accepted successfully")

    # 8. Test invitation reuse
    expect_error(
        lambda: accept_invitation(
            db,
            token=invitation_result["token"],
            user_id=another_member.id
        ),
        ValueError
    )

    print("PASS: Reused invitation rejection")

    # 9. Test already existing group member
    second_invitation = create_invitation(
        db,
        group_id=group.id,
        invited_by=admin.id
    )

    expect_error(
        lambda: accept_invitation(
            db,
            token=second_invitation["token"],
            user_id=admin.id
        ),
        ValueError
    )

    print("PASS: Existing member rejection")

    # 10. Create an expired invitation
    expired_token = "expired-test-" + uuid4().hex

    expired_invitation = Invitation(
        group_id=group.id,
        invited_by=admin.id,
        token_hash=hash_token(expired_token),
        expires_at=datetime.now(timezone.utc) - timedelta(days=1)
    )

    db.add(expired_invitation)
    db.commit()

    # 11. Test expired invitation rejection
    expect_error(
        lambda: accept_invitation(
            db,
            token=expired_token,
            user_id=member.id
        ),
        ValueError
    )

    print("PASS: Expired invitation rejection")

    # 12. Test invalid invitation token
    expect_error(
        lambda: accept_invitation(
            db,
            token="invalid-token",
            user_id=member.id
        ),
        ValueError
    )

    print("PASS: Invalid invitation rejection")

    print("\nAll invitation tests passed!")

finally:
    db.close()
