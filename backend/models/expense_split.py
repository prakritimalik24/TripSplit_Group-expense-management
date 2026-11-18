
import uuid
from decimal import Decimal

from sqlalchemy import Numeric, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base


class ExpenseSplit(Base):
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
