import uuid

from sqlalchemy import String, Boolean , DateTime , func
from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import Uuid
from backend.db.base import Base

class User(Base):
    groups_created = relationship("Group" , back_populates="creator")
    memberships = relationship("GroupMember" , back_populates="user")

    expenses_paid = relationship(
    "Expense",
    back_populates="payer",
    foreign_keys="Expense.paid_by"
    )

    expense_splits = relationship("ExpenseSplit", back_populates="user")

    settlements_sent = relationship(
        "Settlement",
        back_populates="payer",
        foreign_keys="Settlement.paid_by"
    )

    settlements_received = relationship(
        "Settlement",
        back_populates="receiver",
        foreign_keys="Settlement.paid_to"
    )

    invitations_sent = relationship("Invitation", back_populates="inviter")

    __tablename__ = "users"

    id:Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    name:Mapped[str] = mapped_column(
        String(100),
        nullable= False
    )

    email:Mapped[str] = mapped_column(
         String(255),
         unique=True,
        nullable= False
            )

    password_hash:Mapped[str] = mapped_column(
        String(255),
        nullable= False
            )

    created_at : Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at : Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )