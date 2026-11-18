
import uuid

from sqlalchemy import String, Text, Date, DateTime, Uuid, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base


class Group(Base):
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
