
from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Group, GroupMember

from backend.services.validation import (
    validate_text,
    validate_date
)


def _validate_group_dates(
    start_date: date | None,
    end_date: date | None
):
    if (
        start_date is not None
        and end_date is not None
        and end_date < start_date
    ):
        raise ValueError(
            "End date cannot be earlier than start date."
        )


def create_group(
    db: Session,
    name: str,
    created_by: UUID,
    description: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None
):

    # Validate group name
    name = validate_text(
        name,
        field_name="Group name",
        max_length=100
    )

    # Validate description
    description = validate_text(
        description if description is not None else "",
        field_name="Group description",
        max_length=1000,
        required=False
    )

    # Validate dates
    start_date = validate_date(
        start_date,
        "Start date"
    )

    end_date = validate_date(
        end_date,
        "End date"
    )

    _validate_group_dates(start_date, end_date)

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


def get_all_groups(
    db: Session,
    user_id: UUID
):

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

    group = get_group_by_id(
        db,
        group_id,
        user_id
    )

    if group is None:
        return None

    admin_statement = select(GroupMember).where(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
        GroupMember.role == "admin"
    )

    admin = db.execute(
        admin_statement
    ).scalar_one_or_none()

    if admin is None:
        raise PermissionError(
            "Only group admins can update the group."
        )

    try:

        # Validate name
        if name is not None:

            group.name = validate_text(
                name,
                field_name="Group name",
                max_length=100
            )

        # Validate description
        if description is not None:

            group.description = validate_text(
                description,
                field_name="Group description",
                max_length=1000,
                required=False
            )

        # Validate dates
        if start_date is not None:

            group.start_date = validate_date(
                start_date,
                "Start date"
            )

        if end_date is not None:

            group.end_date = validate_date(
                end_date,
                "End date"
            )

        # Validate the final date range,
        # including dates that were not updated.
        _validate_group_dates(
            group.start_date,
            group.end_date
        )

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

    group = get_group_by_id(
        db,
        group_id,
        user_id
    )

    if group is None:
        return None

    admin_statement = select(GroupMember).where(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
        GroupMember.role == "admin"
    )

    admin = db.execute(
        admin_statement
    ).scalar_one_or_none()

    if admin is None:
        raise PermissionError(
            "Only group admins can archive the group."
        )

    try:

        group.status = "archived"

        db.commit()
        db.refresh(group)

        return group

    except Exception:
        db.rollback()
        raise
