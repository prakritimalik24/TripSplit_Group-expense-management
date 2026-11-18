
import uuid
from decimal import Decimal

from sqlalchemy import Numeric, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column , relationship
from sqlalchemy import UniqueConstraint, CheckConstraint
from backend.db.base import Base


class ExpenseSplit(Base):
    __table_args__ = (
    UniqueConstraint("expense_id", "user_id", name="uq_expense_split"),
    CheckConstraint("amount >= 0", name="check_split_amount"),
)
    expense = relationship("Expense", back_populates="splits")
    user = relationship("User", back_populates="expense_splits")

    __tablename__ = "expense_splits"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    expense_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("expenses.id"),
        nullable=False
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
