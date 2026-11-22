
import hashlib
import secrets

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models import Invitation, GroupMember


# Helper: Hash invitation token
def _hash_invitation_token(token: str) -> str:

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


# 1. Create a group invitation
def create_invitation(
    db: Session,
    group_id: UUID,
    invited_by: UUID,
    expires_in_days: int = 7
):

    if expires_in_days <= 0:
        raise ValueError("Invitation expiry must be positive.")

    # Check whether inviter is a group admin
    membership = db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == invited_by
        )
    ).scalar_one_or_none()

    if membership is None or membership.role != "admin":
        raise PermissionError(
            "Only group admins can create invitations."
        )

    # Generate a secure random token
    raw_token = secrets.token_urlsafe(32)

    # Store only its hash
    token_hash = _hash_invitation_token(raw_token)

    # Calculate expiration time
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=expires_in_days
    )

    invitation = Invitation(
        group_id=group_id,
        invited_by=invited_by,
        token_hash=token_hash,
        expires_at=expires_at
    )

    try:
        db.add(invitation)
        db.commit()
        db.refresh(invitation)

        # Return raw token only once
        return {
            "invitation_id": invitation.id,
            "group_id": invitation.group_id,
            "token": raw_token,
            "expires_at": invitation.expires_at
        }

    except Exception:
        db.rollback()
        raise



def accept_invitation(
    db: Session,
    token: str,
    user_id: UUID
):
    if not token:
        raise ValueError("Invitation token is required.")

    token_hash = _hash_invitation_token(token)

    statement = (
        select(Invitation)
        .where(Invitation.token_hash == token_hash)
        .with_for_update()
    )

    try:
        invitation = db.execute(
            statement
        ).scalar_one_or_none()

        if invitation is None:
            raise ValueError("Invalid invitation token.")

        if invitation.used_at is not None:
            raise ValueError("This invitation has already been used.")

        if datetime.now(timezone.utc) >= invitation.expires_at:
            raise ValueError("This invitation has expired.")

        existing_membership = db.execute(
            select(GroupMember).where(
                GroupMember.group_id == invitation.group_id,
                GroupMember.user_id == user_id
            )
        ).scalar_one_or_none()

        if existing_membership is not None:
            raise ValueError("You are already a member of this group.")

        new_membership = GroupMember(
            group_id=invitation.group_id,
            user_id=user_id,
            role="member"
        )

        db.add(new_membership)
        invitation.used_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(new_membership)

        return new_membership

    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Invitation could not be accepted. It may already be used."
        )

    except Exception:
        db.rollback()
        raise
