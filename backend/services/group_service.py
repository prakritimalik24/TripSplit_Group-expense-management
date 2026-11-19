
from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Group, GroupMember


def create_group(
    db: Session,
    name: str,
    created_by: UUID,
    description: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None
):
    new_group = Group(
        name=name,
        created_by=created_by,
        description=description,
        start_date=start_date,
        end_date=end_date
    )

    try:
        db.add(new_group)
        db.flush()

        creator_membership = GroupMember(
            group_id=new_group.id,
            user_id=created_by,
            role="admin"
        )

        db.add(creator_membership)

        db.commit()
        db.refresh(new_group)

        return new_group

    except Exception:
        db.rollback()
        raise


def get_group_by_id(
    db: Session,
    group_id: UUID,
    user_id: UUID
):
    statement = (
        select(Group)
        .join(GroupMember)
        .where(
            Group.id == group_id,
            GroupMember.user_id == user_id
        )
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


def get_all_groups(db: Session, user_id: UUID):

    statement = (
        select(Group)
        .join(GroupMember)
        .where(GroupMember.user_id == user_id)
    )

    result = db.execute(statement)

    return result.scalars().all()


def update_group(
    db: Session,
    group_id: UUID,
    user_id: UUID,
    name: str | None = None,
    description: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None
):
    group = get_group_by_id(db, group_id, user_id)

    if group is None:
        return None

    admin_statement = select(GroupMember).where(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
        GroupMember.role == "admin"
    )

    admin = db.execute(admin_statement).scalar_one_or_none()

    if admin is None:
        raise PermissionError("Only group admins can update the group.")

    try:
        if name is not None:
            group.name = name

        if description is not None:
            group.description = description

        if start_date is not None:
            group.start_date = start_date

        if end_date is not None:
            group.end_date = end_date

        db.commit()
        db.refresh(group)

        return group

    except Exception:
        db.rollback()
        raise


def delete_group(
    db: Session,
    group_id: UUID,
    user_id: UUID
):
    group = get_group_by_id(db, group_id, user_id)

    if group is None:
        return None

    admin_statement = select(GroupMember).where(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
        GroupMember.role == "admin"
    )

    admin = db.execute(admin_statement).scalar_one_or_none()

    if admin is None:
        raise PermissionError("Only group admins can archive the group.")

    try:
        group.status = "archived"

        db.commit()
        db.refresh(group)

        return group

    except Exception:
        db.rollback()
        raise
