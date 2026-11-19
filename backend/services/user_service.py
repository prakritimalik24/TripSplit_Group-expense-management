from sqlalchemy.orm import Session

from backend.models import User
from sqlalchemy import select

def create_user(
        db:Session,
        name:str,
        email:str,
        password_hash:str
):
    new_user = User(
        name=name,
        email=email,
        password_hash=password_hash
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except Exception:
        db.rollback()
        raise



def get_user_by_email(db: Session, email: str):

    statement = select(User).where(User.email == email)

    result = db.execute(statement)

    return result.scalar_one_or_none()



def get_user_by_id(db: Session, user_id):

    return db.get(User, user_id)



def update_user(
    db: Session,
    user_id,
    name: str | None = None,
    email: str | None = None
):
    user = db.get(User, user_id)

    if user is None:
        return None

    try:
        if name is not None:
            user.name = name

        if email is not None:
            user.email = email

        db.commit()
        db.refresh(user)

        return user

    except Exception:
        db.rollback()
        raise



def deactivate_user(db: Session, user_id):

    user = db.get(User, user_id)

    if user is None:
        return None

    try:
        user.is_active = False

        db.commit()
        db.refresh(user)

        return user

    except Exception:
        db.rollback()
        raise
