
import uuid
from decimal import Decimal

from sqlalchemy import Numeric, DateTime, Uuid, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column ,relationship
from sqlalchemy import CheckConstraint
from backend.db.base import Base


class Settlement(Base):
    __table_args__ = (
    CheckConstraint("amount > 0", name="check_settlement_amount"),
    CheckConstraint("paid_by != paid_to", name="check_different_users"),
)
    
    group = relationship("Group", back_populates="settlements")

    payer = relationship(
        "User",
        back_populates="settlements_sent",
        foreign_keys="Settlement.paid_by"
    )

    receiver = relationship(
        "User",
        back_populates="settlements_received",
        foreign_keys="Settlement.paid_to"
    )

    __tablename__ = "settlements"

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

    paid_to: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    settled_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
