
import uuid

from sqlalchemy import String, Text, Date, DateTime, Uuid, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column , relationship
from sqlalchemy import CheckConstraint
from backend.db.base import Base


class Group(Base):
    __table_args__ = (
        CheckConstraint(
            "start_date IS NULL OR end_date IS NULL OR end_date >= start_date",
            name="check_group_dates"
        ),
    )
    creator = relationship("User", back_populates="groups_created")
    members = relationship("GroupMember", back_populates="group")
    expenses = relationship("Expense", back_populates="group")
    settlements = relationship("Settlement", back_populates="group")
    invitations = relationship("Invitation", back_populates="group")

    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False
    )

    start_date: Mapped[Date | None] = mapped_column(
        Date,
        nullable=True
    )

    end_date: Mapped[Date | None] = mapped_column(
        Date,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
