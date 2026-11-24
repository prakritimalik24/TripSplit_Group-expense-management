
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Expense, ExpenseSplit, GroupMember
from backend.services.validation import validate_amount


CENT = Decimal("0.01")


def _get_expense_for_member(
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

    return db.execute(statement).scalar_one_or_none()


def _validate_split_access(
    db: Session,
    expense: Expense,
    user_id: UUID
):

    membership = db.execute(
        select(GroupMember).where(
            GroupMember.group_id == expense.group_id,
            GroupMember.user_id == user_id
        )
    ).scalar_one_or_none()

    if membership is None:
        raise PermissionError(
            "You are not a member of this group."
        )

    if expense.paid_by != user_id and membership.role != "admin":
        raise PermissionError(
            "Only the payer or group admin can create expense splits."
        )


def _validate_participants(
    db: Session,
    group_id: UUID,
    participant_ids: list[UUID]
):

    if not participant_ids:
        raise ValueError(
            "At least one participant is required."
        )

    if len(participant_ids) != len(set(participant_ids)):
        raise ValueError(
            "Duplicate participants are not allowed."
        )

    statement = select(GroupMember.user_id).where(
        GroupMember.group_id == group_id,
        GroupMember.user_id.in_(participant_ids)
    )

    valid_ids = set(
        db.execute(statement).scalars().all()
    )

    if valid_ids != set(participant_ids):
        raise ValueError(
            "All split participants must belong to the group."
        )


def _check_existing_splits(
    db: Session,
    expense_id: UUID
):

    existing = db.execute(
        select(ExpenseSplit).where(
            ExpenseSplit.expense_id == expense_id
        )
    ).scalars().first()

    if existing is not None:
        raise ValueError(
            "Splits already exist for this expense."
        )


def create_equal_splits(
    db: Session,
    expense_id: UUID,
    user_id: UUID,
    participant_ids: list[UUID],
    commit: bool = True
):

    expense = _get_expense_for_member(
        db,
        expense_id,
        user_id
    )

    if expense is None:
        raise ValueError(
            "Expense not found or access denied."
        )

    _validate_split_access(db, expense, user_id)

    _validate_participants(
        db,
        expense.group_id,
        participant_ids
    )

    _check_existing_splits(db, expense_id)

    # Convert amount into cents to avoid floating-point errors
    total_cents = int(expense.amount * 100)

    base_cents, remainder = divmod(
        total_cents,
        len(participant_ids)
    )

    split_records = []

    for index, participant_id in enumerate(participant_ids):

        participant_cents = base_cents

        if index < remainder:
            participant_cents += 1

        share = Decimal(participant_cents) / 100

        split_records.append(
            ExpenseSplit(
                expense_id=expense_id,
                user_id=participant_id,
                amount=share
            )
        )

    try:

        db.add_all(split_records)

        if commit:
            db.commit()
        else:
            db.flush()

        return split_records

    except Exception:
        db.rollback()
        raise


def create_custom_splits(
    db: Session,
    expense_id: UUID,
    user_id: UUID,
    splits: list[tuple[UUID, Decimal]],
    commit: bool = True
):

    expense = _get_expense_for_member(
        db,
        expense_id,
        user_id
    )

    if expense is None:
        raise ValueError(
            "Expense not found or access denied."
        )

    _validate_split_access(db, expense, user_id)

    if not splits:
        raise ValueError(
            "At least one split is required."
        )

    participant_ids = [
        participant_id
        for participant_id, _ in splits
    ]

    _validate_participants(
        db,
        expense.group_id,
        participant_ids
    )

    _check_existing_splits(db, expense_id)

    normalized_splits = []

    for participant_id, amount in splits:

        amount = validate_amount(
            amount,
            "Split amount"
        )

        normalized_splits.append(
            (participant_id, amount)
        )

    total = sum(
        (amount for _, amount in normalized_splits),
        Decimal("0.00")
    )

    if total != expense.amount:
        raise ValueError(
            f"Split total {total} does not match "
            f"expense amount {expense.amount}."
        )

    split_records = [
        ExpenseSplit(
            expense_id=expense_id,
            user_id=participant_id,
            amount=amount
        )
        for participant_id, amount in normalized_splits
    ]

    try:

        db.add_all(split_records)

        if commit:
            db.commit()
        else:
            db.flush()

        return split_records

    except Exception:
        db.rollback()
        raise
