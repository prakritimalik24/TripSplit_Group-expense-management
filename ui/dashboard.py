
import streamlit as st
import pandas as pd
import logging

from uuid import UUID
from datetime import datetime, timezone, timedelta

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from backend.db.session import SessionLocal
from backend.services.group_service import get_all_groups
from backend.models.expense import Expense
from backend.models.expense_split import ExpenseSplit


logger = logging.getLogger(__name__)


def render_dashboard():

    user = st.session_state.user
    user_id = UUID(user["id"])

    # --------------------------------
    # WELCOME SECTION
    # --------------------------------

    st.title(f"Good to see you, {user['name']}!")

    st.caption(
        "Your crew, your plans, your expenses — "
        "everything in one place."
    )

    st.divider()

    db = SessionLocal()

    try:

        # --------------------------------
        # 1. FETCH USER GROUPS
        # --------------------------------

        groups = get_all_groups(
            db,
            user_id=user_id
        )

        group_ids = [group.id for group in groups]

        # --------------------------------
        # 2. YOUR SNAPSHOT
        # --------------------------------

        st.subheader("Your Snapshot")

        st.caption(
            "A quick look at your shared spending."
        )

        if not group_ids:

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Groups You're In",
                    0
                )

            with col2:
                st.metric(
                    "Total Shared Spending",
                    "₹0.00"
                )

            with col3:
                st.metric(
                    "Your Share of Expenses",
                    "₹0.00"
                )

            st.info(
                "Your next adventure starts here! "
                "Create a group or join your friends "
                "to start tracking shared expenses."
            )

            return

        # --------------------------------
        # 3. TOTAL GROUP EXPENSES
        # --------------------------------

        total_expenses = (
            db.query(
                func.coalesce(func.sum(Expense.amount), 0)
            )
            .filter(
                Expense.group_id.in_(group_ids)
            )
            .scalar()
        )

        # --------------------------------
        # 4. USER'S TOTAL SHARE
        # --------------------------------

        user_share = (
            db.query(
                func.coalesce(func.sum(ExpenseSplit.amount), 0)
            )
            .join(
                Expense,
                ExpenseSplit.expense_id == Expense.id
            )
            .filter(
                Expense.group_id.in_(group_ids),
                ExpenseSplit.user_id == user_id
            )
            .scalar()
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Groups You're In",
                len(groups)
            )

        with col2:
            st.metric(
                "Total Shared Spending",
                f"₹{float(total_expenses):,.2f}"
            )

        with col3:
            st.metric(
                "Your Share of Expenses",
                f"₹{float(user_share):,.2f}"
            )

        st.divider()

        # --------------------------------
        # 5. MONTHLY SPENDING TREND
        # --------------------------------

        st.subheader("Your Spending Journey")

        st.caption(
            "See how your group's expenses have changed "
            "over the last six months."
        )

        six_months_ago = (
            datetime.now(timezone.utc)
            - timedelta(days=180)
        )

        monthly_data = (
            db.query(
                func.extract(
                    "year", Expense.expense_date
                ).label("year"),

                func.extract(
                    "month", Expense.expense_date
                ).label("month"),

                func.sum(
                    Expense.amount
                ).label("amount")
            )
            .filter(
                Expense.group_id.in_(group_ids),
                Expense.expense_date >= six_months_ago
            )
            .group_by(
                func.extract("year", Expense.expense_date),
                func.extract("month", Expense.expense_date)
            )
            .order_by(
                func.extract("year", Expense.expense_date),
                func.extract("month", Expense.expense_date)
            )
            .all()
        )

        if monthly_data:

            monthly_df = pd.DataFrame([
                {
                    "Month": datetime(
                        int(year),
                        int(month),
                        1
                    ).strftime("%b %Y"),

                    "Amount": float(amount)
                }
                for year, month, amount in monthly_data
            ])

            st.bar_chart(
                monthly_df.set_index("Month"),
                color="#8CABBE"
            )

        else:

            st.info(
                "Your spending timeline will appear here "
                "once your groups start adding expenses."
            )

        # --------------------------------
        # 6. CATEGORY-WISE EXPENSES
        # --------------------------------

        st.subheader("Where Your Money Goes")

        st.caption(
            "Understand which categories account "
            "for most of your shared spending."
        )

        category_data = (
            db.query(
                Expense.category,
                func.sum(
                    Expense.amount
                ).label("amount")
            )
            .filter(
                Expense.group_id.in_(group_ids)
            )
            .group_by(
                Expense.category
            )
            .order_by(
                func.sum(Expense.amount).desc()
            )
            .all()
        )

        if category_data:

            category_df = pd.DataFrame([
                {
                    "Category": category or "Uncategorized",
                    "Amount": float(amount)
                }
                for category, amount in category_data
            ])

            st.bar_chart(
                category_df.set_index("Category"),
                color="#4E6E58"
            )

        else:

            st.info(
                "Category insights will appear here "
                "as you add expenses."
            )

        # --------------------------------
        # 7. YOUR GROUPS
        # --------------------------------

        st.divider()

        st.subheader("Your Travel Circles")

        st.caption(
            "All the groups you're sharing expenses with."
        )

        for group in groups:

            with st.container(border=True):

                st.subheader(group.name)

                if group.description:
                    st.write(group.description)

                else:
                    st.caption(
                        "No group description added yet."
                    )

    except (ValueError, PermissionError) as error:

        db.rollback()
        st.error(str(error))

    except SQLAlchemyError:

        db.rollback()

        logger.exception(
            "Database error while loading dashboard."
        )

        st.error(
            "Unable to load dashboard information. "
            "Please try again later."
        )

    except Exception:

        db.rollback()

        logger.exception(
            "Unexpected error while loading dashboard."
        )

        st.error(
            "Something went wrong while loading your dashboard. "
            "Please try again."
        )

    finally:
        db.close()
