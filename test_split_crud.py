
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from backend.db.session import SessionLocal
from backend.models import GroupMember
from backend.services.user_service import create_user
from backend.services.group_service import create_group
from backend.services.expense_service import create_expense
from backend.services.split_service import (
    create_equal_splits,
    create_custom_splits
)


db = SessionLocal()

try:
    # 1. Create three users
    users = []

    for i in range(3):
        user = create_user(
            db,
            name=f"Split User {i + 1}",
            email=f"split_{uuid4().hex[:8]}@example.com",
            password_hash="test_hash"
        )
        users.append(user)

    print("PASS: Three users created")

    # 2. Create group using first user
    group = create_group(
        db,
        name="Split Test Group",
        created_by=users[0].id
    )

    # Add remaining two users to group
    memberships = [
        GroupMember(
            group_id=group.id,
            user_id=user.id,
            role="member"
        )
        for user in users[1:]
    ]

    db.add_all(memberships)
    db.commit()

    print("PASS: All users added to group")

    # 3. Create expense for equal splitting
    expense = create_expense(
        db,
        group_id=group.id,
        paid_by=users[0].id,
        title="Dinner Bill",
        amount=Decimal("100.00"),
        expense_date=datetime.now(timezone.utc)
    )

    # 4. Equal splitting
    equal_splits = create_equal_splits(
        db,
        expense.id,
        users[0].id,
        [user.id for user in users]
    )

    equal_total = sum(
        (split.amount for split in equal_splits),
        Decimal("0.00")
    )

    assert equal_total == Decimal("100.00")
    assert len(equal_splits) == 3

    print("PASS: Equal splitting")
    print("Equal shares:", [s.amount for s in equal_splits])
    print("Equal split total:", equal_total)

    # 5. Create another expense for custom splitting
    custom_expense = create_expense(
        db,
        group_id=group.id,
        paid_by=users[0].id,
        title="Hotel Bill",
        amount=Decimal("900.00"),
        expense_date=datetime.now(timezone.utc)
    )

    # 6. Custom splitting
    custom_splits = create_custom_splits(
        db,
        custom_expense.id,
        users[0].id,
        [
            (users[0].id, Decimal("500.00")),
            (users[1].id, Decimal("250.00")),
            (users[2].id, Decimal("150.00"))
        ]
    )

    custom_total = sum(
        (split.amount for split in custom_splits),
        Decimal("0.00")
    )

    assert custom_total == Decimal("900.00")
    assert len(custom_splits) == 3

    print("PASS: Custom splitting")
    print("Custom shares:", [s.amount for s in custom_splits])
    print("Custom split total:", custom_total)

    print("\nAll split service tests passed!")

finally:
    db.close()
