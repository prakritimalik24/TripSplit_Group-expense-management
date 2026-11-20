
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from backend.db.session import SessionLocal
from backend.services.user_service import create_user
from backend.services.group_service import create_group
from backend.services.expense_service import (
    create_expense,
    get_expense_by_id,
    get_group_expenses,
    update_expense,
    delete_expense
)


db = SessionLocal()

try:
    # Create test user
    email = f"expense_{uuid4().hex[:8]}@example.com"

    user = create_user(
        db,
        name="Expense Test User",
        email=email,
        password_hash="test_hash"
    )

    print("PASS: User created")

    # Create test group
    group = create_group(
        db,
        name="Expense Test Group",
        created_by=user.id
    )

    print("PASS: Group created")

    # Create expense
    expense = create_expense(
        db,
        group_id=group.id,
        paid_by=user.id,
        title="Dinner",
        amount=Decimal("1200.00"),
        expense_date=datetime.now(timezone.utc),
        category="Food"
    )

    print("PASS: Expense created")

    # Get expense by ID
    found_expense = get_expense_by_id(
        db,
        expense.id,
        user.id
    )

    assert found_expense is not None
    print("PASS: Get expense by ID")

    # Get all group expenses
    expenses = get_group_expenses(
        db,
        group.id,
        user.id
    )

    assert any(e.id == expense.id for e in expenses)
    print("PASS: Get group expenses")

    # Update expense
    updated_expense = update_expense(
        db,
        expense.id,
        user.id,
        title="Updated Dinner"
    )

    assert updated_expense.title == "Updated Dinner"
    print("PASS: Update expense")

    # Delete expense
    deleted = delete_expense(
        db,
        expense.id,
        user.id
    )

    assert deleted is True
    print("PASS: Delete expense")

    # Verify deletion
    result = get_expense_by_id(
        db,
        expense.id,
        user.id
    )

    assert result is None
    print("PASS: Verify expense deletion")

    print("\nAll expense CRUD tests passed!")

finally:
    db.close()
