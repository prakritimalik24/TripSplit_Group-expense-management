
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.models import Expense, ExpenseSplit, GroupMember

def _get_membership(db: Session, group_id: UUID, user_id: UUID):
    statement = select(GroupMember).where(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    )

    return db.execute(statement).scalar_one_or_none()

def create_expense(
    db: Session,
    group_id: UUID,
    paid_by: UUID,
    title: str,
    amount: Decimal,
    expense_date: datetime,
    category: str | None = None
):
    amount = Decimal(str(amount))

    if amount <= 0:
        raise ValueError("Expense amount must be positive.")

    if amount != amount.quantize(Decimal("0.01")):
        raise ValueError("Expense amount can have at most 2 decimal places.")

    if not title.strip():
        raise ValueError("Expense title cannot be empty.")

    membership = _get_membership(db, group_id, paid_by)

    if membership is None:
        raise PermissionError("Payer must be a group member.")

    new_expense = Expense(
        group_id=group_id,
        paid_by=paid_by,
        title=title.strip(),
        amount=amount,
        category=category,
        expense_date=expense_date
    )

    try:
        db.add(new_expense)
        db.commit()
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
    membership = _get_membership(db, group_id, user_id)

    if membership is None:
        raise PermissionError("You are not a member of this group.")

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
    expense = get_expense_by_id(db, expense_id, user_id)

    if expense is None:
        return None

    membership = _get_membership(db, expense.group_id, user_id)

    if expense.paid_by != user_id and membership.role != "admin":
        raise PermissionError("Only the payer or group admin can update this expense.")

    try:
        if title is not None:
            if not title.strip():
                raise ValueError("Expense title cannot be empty.")
            expense.title = title.strip()

        if amount is not None:
            amount = Decimal(str(amount))

            if amount <= 0:
                raise ValueError("Expense amount must be positive.")

            if amount != amount.quantize(Decimal("0.01")):
                raise ValueError("Expense amount can have at most 2 decimal places.")

            existing_splits = db.execute(
                select(ExpenseSplit).where(
                    ExpenseSplit.expense_id == expense_id
                )
            ).scalars().first()

            if existing_splits is not None:
                raise ValueError(
                    "Cannot change expense amount after splits are created."
                )

            expense.amount = amount

        if category is not None:
            expense.category = category

        if expense_date is not None:
            expense.expense_date = expense_date

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
    expense = get_expense_by_id(db, expense_id, user_id)

    if expense is None:
        return False

    membership = _get_membership(db, expense.group_id, user_id)

    if expense.paid_by != user_id and membership.role != "admin":
        raise PermissionError("Only the payer or group admin can delete this expense.")

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