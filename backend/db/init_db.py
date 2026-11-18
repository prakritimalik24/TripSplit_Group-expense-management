from backend.db.base import Base
from backend.db.connection import engine

from backend.models.user import User
from backend.models.group import Group
from backend.models.group_member import GroupMember
from backend.models.expense import Expense
from backend.models.expense_split import ExpenseSplit
from backend.models.settlement import Settlement
from backend.models.invitation import Invitation

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("All database tables created successfully!")


if __name__ == "__main__":
    create_tables()