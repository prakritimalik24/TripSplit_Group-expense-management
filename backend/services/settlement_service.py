
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from backend.models import (
    GroupMember,
    Expense,
    ExpenseSplit,
    Settlement
)


CENT = Decimal("0.01")


# 1. Calculate net balance of every group member
def calculate_group_balances(
    db: Session,
    group_id: UUID,
    user_id: UUID
):
    # Check whether requesting user belongs to the group
    membership = db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        )
    ).scalar_one_or_none()

    if membership is None:
        raise PermissionError("You are not a member of this group.")

    # Get all group members
    member_ids = db.execute(
        select(GroupMember.user_id).where(
            GroupMember.group_id == group_id
        )
    ).scalars().all()

    balances = {
        member_id: Decimal("0.00")
        for member_id in member_ids
    }

    # Calculate total amount paid by each member
    paid_totals = db.execute(
        select(
            Expense.paid_by,
            func.sum(Expense.amount)
        )
        .where(Expense.group_id == group_id)
        .group_by(Expense.paid_by)
    ).all()

    for member_id, amount in paid_totals:
        balances[member_id] += amount

    # Calculate total amount owed by each member
    owed_totals = db.execute(
        select(
            ExpenseSplit.user_id,
            func.sum(ExpenseSplit.amount)
        )
        .join(
            Expense,
            ExpenseSplit.expense_id == Expense.id
        )
        .where(Expense.group_id == group_id)
        .group_by(ExpenseSplit.user_id)
    ).all()

    for member_id, amount in owed_totals:
        balances[member_id] -= amount

    # Account for money sent in previous settlements
    sent_totals = db.execute(
        select(
            Settlement.paid_by,
            func.sum(Settlement.amount)
        )
        .where(Settlement.group_id == group_id)
        .group_by(Settlement.paid_by)
    ).all()

    for member_id, amount in sent_totals:
        balances[member_id] += amount

    # Account for money received in previous settlements
    received_totals = db.execute(
        select(
            Settlement.paid_to,
            func.sum(Settlement.amount)
        )
        .where(Settlement.group_id == group_id)
        .group_by(Settlement.paid_to)
    ).all()

    for member_id, amount in received_totals:
        balances[member_id] -= amount

    return balances


# 2. Simplify debts using a Greedy Algorithm
def simplify_debts(balances: dict):

    creditors = []
    debtors = []

    # Separate people who should receive and pay money
    for user_id, balance in balances.items():

        balance = Decimal(str(balance))

        if balance > 0:
            creditors.append({
                "user_id": user_id,
                "amount": balance
            })

        elif balance < 0:
            debtors.append({
                "user_id": user_id,
                "amount": abs(balance)
            })

    # Total credits and debts must balance
    total_credit = sum(
        (person["amount"] for person in creditors),
        Decimal("0.00")
    )

    total_debt = sum(
        (person["amount"] for person in debtors),
        Decimal("0.00")
    )

    if total_credit != total_debt:
        raise ValueError("Group balances do not add up to zero.")

    transactions = []

    creditor_index = 0
    debtor_index = 0

    # Match debtors with creditors
    while (
        creditor_index < len(creditors)
        and debtor_index < len(debtors)
    ):

        creditor = creditors[creditor_index]
        debtor = debtors[debtor_index]

        # Transfer the smaller outstanding amount
        amount = min(
            creditor["amount"],
            debtor["amount"]
        )

        transactions.append({
            "paid_by": debtor["user_id"],
            "paid_to": creditor["user_id"],
            "amount": amount
        })

        # Reduce both outstanding balances
        creditor["amount"] -= amount
        debtor["amount"] -= amount

        # Move to the next creditor if fully paid
        if creditor["amount"] == 0:
            creditor_index += 1

        # Move to the next debtor if fully paid
        if debtor["amount"] == 0:
            debtor_index += 1

    return transactions


# 3. Record a settlement in the database
def record_settlement(
    db: Session,
    group_id: UUID,
    paid_by: UUID,
    paid_to: UUID,
    amount: Decimal,
    recorded_by: UUID
):

    amount = Decimal(str(amount))

    if amount <= 0:
        raise ValueError("Settlement amount must be positive.")

    if amount != amount.quantize(CENT):
        raise ValueError("Settlement can have at most 2 decimal places.")

    if paid_by == paid_to:
        raise ValueError("A user cannot pay themselves.")

    # Verify all three users belong to the group
    memberships = db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id.in_([
                paid_by, paid_to, recorded_by
            ])
        )
    ).scalars().all()

    membership_map = {
        membership.user_id: membership
        for membership in memberships
    }

    if any(
        user_id not in membership_map
        for user_id in (paid_by, paid_to, recorded_by)
    ):
        raise PermissionError("All users must belong to this group.")

    # Only the payer, receiver, or group admin can record payment
    recorder_membership = membership_map[recorded_by]

    if (
        recorded_by not in (paid_by, paid_to)
        and recorder_membership.role != "admin"
    ):
        raise PermissionError("You cannot record this settlement.")

    # Get current balances before recording payment
    balances = calculate_group_balances(
        db,
        group_id,
        recorded_by
    )

    payer_balance = balances[paid_by]
    receiver_balance = balances[paid_to]

    # Verify that payer owes money and receiver should receive it
    if payer_balance >= 0 or receiver_balance <= 0:
        raise ValueError("Invalid settlement participants.")

    # Prevent overpayment
    maximum_amount = min(
        abs(payer_balance),
        receiver_balance
    )

    if amount > maximum_amount:
        raise ValueError(
            f"Settlement exceeds the outstanding amount of "
            f"{maximum_amount}."
        )

    new_settlement = Settlement(
        group_id=group_id,
        paid_by=paid_by,
        paid_to=paid_to,
        amount=amount
    )

    try:
        db.add(new_settlement)
        db.commit()
        db.refresh(new_settlement)

        return new_settlement

    except Exception:
        db.rollback()
        raise


# 4. Get all settlements of a group
def get_group_settlements(
    db: Session,
    group_id: UUID,
    user_id: UUID
):

    membership = db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        )
    ).scalar_one_or_none()

    if membership is None:
        raise PermissionError("You are not a member of this group.")

    statement = (
        select(Settlement)
        .where(Settlement.group_id == group_id)
        .order_by(Settlement.settled_at.desc())
    )

    return db.execute(statement).scalars().all()


# 5. Get settlement history of a particular member
def get_user_settlements(
    db: Session,
    group_id: UUID,
    user_id: UUID
):

    membership = db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        )
    ).scalar_one_or_none()

    if membership is None:
        raise PermissionError("You are not a member of this group.")

    statement = (
        select(Settlement)
        .where(
            Settlement.group_id == group_id,
            or_(
                Settlement.paid_by == user_id,
                Settlement.paid_to == user_id
            )
        )
        .order_by(Settlement.settled_at.desc())
    )

    return db.execute(statement).scalars().all()
