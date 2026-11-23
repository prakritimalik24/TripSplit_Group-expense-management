
import streamlit as st

from uuid import UUID
from decimal import Decimal
from datetime import datetime, time, timezone

from sqlalchemy import select

from backend.db.session import SessionLocal
from backend.models import GroupMember, ExpenseSplit

from backend.services.group_service import get_all_groups

from backend.services.expense_service import (
    create_expense,
    get_group_expenses
)

from backend.services.split_service import (
    create_equal_splits,
    create_custom_splits
)


def render_expenses():

    user_id = UUID(st.session_state.user["id"])

    st.title("💰 Expense Management")
    st.caption("Add expenses and split them with your group.")

    db = SessionLocal()

    try:
        groups = get_all_groups(db, user_id)

        if not groups:
            st.info("Create or join a group before adding expenses.")
            return

        selected_group = st.selectbox(
            "Select Group",
            options=groups,
            format_func=lambda group: group.name,
            key="expense_group"
        )

        group_id = selected_group.id

        # Fetch group members
        members = db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id
            )
        ).scalars().all()

        member_names = {
            member.user_id: member.user.name
            for member in members
        }

        member_ids = list(member_names.keys())

        st.divider()

        add_tab, history_tab = st.tabs(
            ["Add Expense", "Expense History"]
        )

        # ==================================
        # 1. ADD EXPENSE
        # ==================================

        with add_tab:

            st.subheader("Add a New Expense")

            participant_ids = st.multiselect(
                "Split this expense between",
                options=member_ids,
                default=member_ids,
                format_func=lambda uid: member_names[uid],
                key=f"participants_{group_id}"
            )

            split_type = st.radio(
                "Choose Split Type",
                ["Equal Split", "Custom Split"],
                horizontal=True,
                key=f"split_type_{group_id}"
            )

            with st.form(f"expense_form_{group_id}"):

                title = st.text_input("Expense Title")

                amount = st.number_input(
                    "Total Amount (₹)",
                    min_value=0.01,
                    value=100.00,
                    step=10.00,
                    format="%.2f"
                )

                category = st.selectbox(
                    "Category",
                    [
                        "Food",
                        "Travel",
                        "Stay",
                        "Shopping",
                        "Activities",
                        "Other"
                    ]
                )

                expense_date = st.date_input(
                    "Expense Date"
                )

                custom_amounts = {}

                if split_type == "Custom Split":

                    st.write("Enter each participant's share:")

                    for uid in participant_ids:

                        custom_amounts[uid] = Decimal(
                            str(
                                st.number_input(
                                    member_names[uid],
                                    min_value=0.01,
                                    value=round(
                                        amount / max(len(participant_ids), 1),
                                        2
                                    ),
                                    step=1.00,
                                    format="%.2f",
                                    key=f"custom_{group_id}_{uid}"
                                )
                            )
                        )

                submit_expense = st.form_submit_button(
                    "Add Expense",
                    use_container_width=True
                )

            if submit_expense:

                if not title.strip():
                    st.warning("Please enter an expense title.")

                elif not participant_ids:
                    st.warning("Select at least one participant.")

                elif split_type == "Custom Split" and (
                    sum(custom_amounts.values(), Decimal("0.00"))
                    != Decimal(str(amount))
                ):
                    st.error(
                        "The sum of individual shares must equal "
                        "the total expense amount."
                    )

                else:

                    try:
                        expense_datetime = datetime.combine(
                            expense_date,
                            time.min,
                            tzinfo=timezone.utc
                        )

                        # Create expense
                        expense = create_expense(
                            db=db,
                            group_id=group_id,
                            paid_by=user_id,
                            title=title.strip(),
                            amount=Decimal(str(amount)),
                            expense_date=expense_datetime,
                            category=category
                        )

                        # Create splits
                        if split_type == "Equal Split":

                            create_equal_splits(
                                db=db,
                                expense_id=expense.id,
                                user_id=user_id,
                                participant_ids=participant_ids
                            )

                        else:

                            splits = [
                                (uid, share)
                                for uid, share in custom_amounts.items()
                            ]

                            create_custom_splits(
                                db=db,
                                expense_id=expense.id,
                                user_id=user_id,
                                splits=splits
                            )

                        st.success(
                            f"Expense '{expense.title}' added successfully!"
                        )

                        st.rerun()

                    except Exception as error:
                        db.rollback()
                        st.error(f"Unable to add expense: {error}")

        # ==================================
        # 2. EXPENSE HISTORY
        # ==================================

        with history_tab:

            st.subheader("Group Expense History")

            expenses = get_group_expenses(
                db=db,
                group_id=group_id,
                user_id=user_id
            )

            if not expenses:

                st.info("No expenses added to this group yet.")

            else:

                for expense in expenses:

                    with st.container(border=True):

                        st.subheader(expense.title)

                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric(
                                "Total Amount",
                                f"₹{expense.amount}"
                            )

                        with col2:
                            st.write(
                                f"**Paid by:** "
                                f"{member_names.get(expense.paid_by, 'Unknown')}"
                            )

                        st.caption(
                            f"Category: {expense.category or 'Other'}"
                        )

                        st.caption(
                            f"Date: {expense.expense_date}"
                        )

                        # Fetch individual splits
                        splits = db.execute(
                            select(ExpenseSplit).where(
                                ExpenseSplit.expense_id == expense.id
                            )
                        ).scalars().all()

                        st.write("**Individual Shares**")

                        if splits:

                            for split in splits:

                                name = member_names.get(
                                    split.user_id,
                                    "Unknown"
                                )

                                st.write(
                                    f"• {name}: ₹{split.amount}"
                                )

                        else:
                            st.caption("No splits recorded.")

    except Exception as error:
        st.error(f"Unable to load expenses: {error}")

    finally:
        db.close()
