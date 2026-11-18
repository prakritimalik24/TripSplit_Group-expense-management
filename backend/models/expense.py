
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String, DateTime, Numeric, Uuid, ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column , relationship
from sqlalchemy import CheckConstraint
from backend.db.base import Base


class Expense(Base):
    __table_args__ = (
        CheckConstraint("amount > 0", name="check_expense_amount"),
    )
    group = relationship("Group", back_populates="expenses")

    payer = relationship(
        "User",
        back_populates="expenses_paid",
        foreign_keys="Expense.paid_by"
    )

    splits = relationship("ExpenseSplit", back_populates="expense")

    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    group_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("groups.id"),
        nullable=False
    )

    paid_by: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    expense_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
