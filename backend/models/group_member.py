
import uuid

from sqlalchemy import String, DateTime, Uuid, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base


class GroupMember(Base):
    __tablename__ = "group_members"

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

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="member",
        nullable=False
    )

    joined_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
