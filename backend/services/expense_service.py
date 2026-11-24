
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.models import Expense, ExpenseSplit, GroupMember

from backend.services.validation import (
    validate_amount,
    validate_text,
    validate_datetime
)


def _get_membership(
    db: Session,
    group_id: UUID,
    user_id: UUID
):
    statement = select(GroupMember).where(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    )

    return db.execute(statement).scalar_one_or_none()


def create_expense(
    db: Session,
    group_id: UUID,
    user_id: UUID,
    paid_by: UUID,
    title: str,
    amount: Decimal,
    expense_date: datetime,
    category: str | None = None,
    commit: bool = True
):

    amount = validate_amount(amount, "Expense amount")

    title = validate_text(
        title,
        field_name="Expense title",
        max_length=150
    )

    category = validate_text(
        category if category is not None else "",
        field_name="Category",
        max_length=50,
        required=False
    )

    expense_date = validate_datetime(
        expense_date,
        field_name="Expense date"
    )

    # Verify acting user membership
    actor_membership = _get_membership(
        db,
        group_id,
        user_id
    )

    if actor_membership is None:
        raise PermissionError(
            "You are not a member of this group."
        )

    # Verify payer membership
    payer_membership = _get_membership(
        db,
        group_id,
        paid_by
    )

    if payer_membership is None:
        raise ValueError(
            "Payer must be a group member."
        )

    # Only payer or admin can create expense on behalf of payer
    if paid_by != user_id and actor_membership.role != "admin":
        raise PermissionError(
            "Only the payer or group admin can create this expense."
        )

    new_expense = Expense(
        group_id=group_id,
        paid_by=paid_by,
        title=title,
        amount=amount,
        category=category,
        expense_date=expense_date
    )

    try:
        db.add(new_expense)

        # Make the expense available to split creation
        db.flush()

        if commit:
            db.commit()
        else:
            # Keep it inside the current transaction
            db.flush()

        db.refresh(new_expense)

        return new_expense

    except Exception:
        db.rollback()
        raise


def get_expense_by_id(
    db: Session,
    expense_id: UUID,
    user_id: UUID
):

    statement = (
        select(Expense)
        .join(
            GroupMember,
            Expense.group_id == GroupMember.group_id
        )
        .where(
            Expense.id == expense_id,
            GroupMember.user_id == user_id
        )
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


def get_group_expenses(
    db: Session,
    group_id: UUID,
    user_id: UUID
):

    membership = _get_membership(
        db,
        group_id,
        user_id
    )

    if membership is None:
        raise PermissionError(
            "You are not a member of this group."
        )

    statement = (
        select(Expense)
        .where(Expense.group_id == group_id)
        .order_by(Expense.expense_date.desc())
    )

    result = db.execute(statement)

    return result.scalars().all()


def update_expense(
    db: Session,
    expense_id: UUID,
    user_id: UUID,
    title: str | None = None,
    amount: Decimal | None = None,
    category: str | None = None,
    expense_date: datetime | None = None
):

    expense = get_expense_by_id(
        db,
        expense_id,
        user_id
    )

    if expense is None:
        return None

    membership = _get_membership(
        db,
        expense.group_id,
        user_id
    )

    if membership is None:
        raise PermissionError(
            "You are not a member of this group."
        )

    if expense.paid_by != user_id and membership.role != "admin":
        raise PermissionError(
            "Only the payer or group admin can update this expense."
        )

    try:

        if title is not None:
            expense.title = validate_text(
                title,
                field_name="Expense title",
                max_length=150
            )

        if amount is not None:

            validated_amount = validate_amount(
                amount,
                "Expense amount"
            )

            existing_splits = db.execute(
                select(ExpenseSplit).where(
                    ExpenseSplit.expense_id == expense_id
                )
            ).scalars().first()

            if existing_splits is not None:
                raise ValueError(
                    "Cannot change expense amount after splits are created."
                )

            expense.amount = validated_amount

        if category is not None:
            expense.category = validate_text(
                category,
                field_name="Category",
                max_length=50,
                required=False
            )

        if expense_date is not None:
            expense.expense_date = validate_datetime(
                expense_date,
                field_name="Expense date"
            )

        db.commit()
        db.refresh(expense)

        return expense

    except Exception:
        db.rollback()
        raise


def delete_expense(
    db: Session,
    expense_id: UUID,
    user_id: UUID
):

    expense = get_expense_by_id(
        db,
        expense_id,
        user_id
    )

    if expense is None:
        return False

    membership = _get_membership(
        db,
        expense.group_id,
        user_id
    )

    if membership is None:
        raise PermissionError(
            "You are not a member of this group."
        )

    if expense.paid_by != user_id and membership.role != "admin":
        raise PermissionError(
            "Only the payer or group admin can delete this expense."
        )

    try:

        db.execute(
            delete(ExpenseSplit).where(
                ExpenseSplit.expense_id == expense_id
            )
        )

        db.delete(expense)
        db.commit()

        return True

    except Exception:
        db.rollback()
        raise
