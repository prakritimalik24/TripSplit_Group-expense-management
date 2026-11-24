
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

    st.title(f"Hello, {user['name']}! ")
    st.caption("Welcome to your TripSplit dashboard.")

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
        # 2. OVERVIEW
        # --------------------------------

        st.subheader("Your Overview")

        if not group_ids:

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Groups", 0)

            with col2:
                st.metric("Total Group Expenses", "₹0.00")

            with col3:
                st.metric("Your Total Share", "₹0.00")

            st.info(
                "You haven't joined any groups yet. "
                "Create or join a group to get started!"
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
                "Total Groups",
                len(groups)
            )

        with col2:
            st.metric(
                "Total Group Expenses",
                f"₹{float(total_expenses):,.2f}"
            )

        with col3:
            st.metric(
                "Your Total Share",
                f"₹{float(user_share):,.2f}"
            )

        st.divider()

        # --------------------------------
        # 5. MONTHLY SPENDING TREND
        # --------------------------------

        st.subheader("📊 Monthly Spending Trend")

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
                "No expense data available for the last six months."
            )

        # --------------------------------
        # 6. CATEGORY-WISE EXPENSES
        # --------------------------------

        st.subheader("📊 Category-wise Spending")

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
                "No category-wise expense data available."
            )

        # --------------------------------
        # 7. YOUR GROUPS
        # --------------------------------

        st.subheader("Your Groups")

        for group in groups:

            with st.container(border=True):

                st.subheader(group.name)

                if group.description:
                    st.write(group.description)

                else:
                    st.caption("No description available.")

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
