
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Uuid, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column , relationship

from backend.db.base import Base


class Invitation(Base):
    group = relationship("Group", back_populates="invitations")

    inviter = relationship("User", back_populates="invitations_sent")

    __tablename__ = "invitations"

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

    invited_by: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False
    )

    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
