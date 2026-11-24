
import streamlit as st
import logging

from uuid import UUID
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from backend.db.session import SessionLocal
from backend.models import GroupMember

from backend.services.group_service import get_all_groups

from backend.services.settlement_service import (
    calculate_group_balances,
    simplify_debts,
    record_settlement,
    get_group_settlements
)


logger = logging.getLogger(__name__)


def render_settlements():

    user_id = UUID(st.session_state.user["id"])

    st.title("💸 Balances & Settlements")
    st.caption("Track who owes whom and settle your expenses.")

    db = SessionLocal()

    try:

        # Select group
        groups = get_all_groups(db, user_id)

        if not groups:
            st.info("Create or join a group first.")
            return

        selected_group = st.selectbox(
            "Select Group",
            options=groups,
            format_func=lambda group: group.name,
            key="settlement_group"
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

        st.divider()

        # Calculate balances
        balances = calculate_group_balances(
            db=db,
            group_id=group_id,
            user_id=user_id
        )

        transactions = simplify_debts(balances)

        # ==================================
        # 1. BALANCE OVERVIEW
        # ==================================

        st.subheader("📊 Group Balance Overview")

        cols = st.columns(3)

        total_members = len(members)

        creditors = sum(
            1 for balance in balances.values()
            if balance > 0
        )

        debtors = sum(
            1 for balance in balances.values()
            if balance < 0
        )

        with cols[0]:
            st.metric("Total Members", total_members)

        with cols[1]:
            st.metric("People Owed", creditors)

        with cols[2]:
            st.metric("People Owing", debtors)

        st.write("### Individual Balances")

        for member_id, balance in balances.items():

            name = member_names.get(member_id, "Unknown")

            with st.container(border=True):

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**{name}**")

                with col2:

                    if balance > 0:
                        st.success(f"+ ₹{balance} to receive")

                    elif balance < 0:
                        st.error(f"- ₹{abs(balance)} to pay")

                    else:
                        st.info("₹0.00 Settled")

        st.divider()

        # ==================================
        # 2. SIMPLIFIED DEBTS
        # ==================================

        st.subheader("🔄 Simplified Debts")

        if transactions:

            st.write(
                "These are the suggested payments to settle "
                "all outstanding group balances."
            )

            for transaction in transactions:

                payer = member_names.get(
                    transaction["paid_by"],
                    "Unknown"
                )

                receiver = member_names.get(
                    transaction["paid_to"],
                    "Unknown"
                )

                amount = transaction["amount"]

                with st.container(border=True):

                    st.write(
                        f"**{payer}** pays **{receiver}**"
                    )

                    st.metric(
                        "Amount",
                        f"₹{amount}"
                    )

        else:

            st.success(
                "Everyone is settled! No pending payments."
            )

        st.divider()

        # ==================================
        # 3. RECORD SETTLEMENT
        # ==================================

        st.subheader("💳 Record a Settlement")

        if transactions:

            transaction_options = transactions

            selected_transaction = st.selectbox(
                "Select a suggested payment",
                options=transaction_options,
                format_func=lambda transaction: (
                    f"{member_names.get(transaction['paid_by'], 'Unknown')} "
                    f"→ {member_names.get(transaction['paid_to'], 'Unknown')} "
                    f"(₹{transaction['amount']})"
                ),
                key=f"payment_{group_id}"
            )

            payer_id = selected_transaction["paid_by"]
            receiver_id = selected_transaction["paid_to"]

            st.write(
                f"**Payer:** {member_names.get(payer_id, 'Unknown')}"
            )

            st.write(
                f"**Receiver:** {member_names.get(receiver_id, 'Unknown')}"
            )

            with st.form(f"settlement_form_{group_id}"):

                amount = st.number_input(
                    "Amount Paid (₹)",
                    min_value=0.01,
                    max_value=float(selected_transaction["amount"]),
                    value=float(selected_transaction["amount"]),
                    step=1.00,
                    format="%.2f"
                )

                submit_settlement = st.form_submit_button(
                    "Record Settlement",
                    use_container_width=True
                )

            if submit_settlement:

                try:

                    settlement = record_settlement(
                        db=db,
                        group_id=group_id,
                        paid_by=payer_id,
                        paid_to=receiver_id,
                        amount=Decimal(str(amount)),
                        recorded_by=user_id
                    )

                    st.success(
                        f"Settlement of ₹{settlement.amount} recorded!"
                    )

                    st.rerun()

                except (ValueError, PermissionError) as error:

                    db.rollback()
                    st.error(str(error))

                except SQLAlchemyError:

                    db.rollback()
                    logger.exception(
                        "Database error while recording settlement."
                    )

                    st.error(
                        "Unable to record settlement due to a database "
                        "error. Please try again."
                    )

                except Exception:

                    db.rollback()
                    logger.exception(
                        "Unexpected error while recording settlement."
                    )

                    st.error(
                        "Something went wrong while recording settlement. "
                        "Please try again."
                    )

        else:

            st.info(
                "No pending payments to record."
            )

        st.divider()

        # ==================================
        # 4. SETTLEMENT HISTORY
        # ==================================

        st.subheader("📜 Settlement History")

        settlements = get_group_settlements(
            db=db,
            group_id=group_id,
            user_id=user_id
        )

        if settlements:

            for settlement in settlements:

                payer = settlement.payer.name
                receiver = settlement.receiver.name

                with st.container(border=True):

                    st.write(
                        f"**{payer}** paid **{receiver}**"
                    )

                    st.metric(
                        "Amount",
                        f"₹{settlement.amount}"
                    )

                    st.caption(
                        f"Date: {settlement.settled_at}"
                    )

        else:

            st.info("No settlements recorded yet.")

    except (ValueError, PermissionError) as error:

        db.rollback()
        st.error(str(error))

    except SQLAlchemyError:

        db.rollback()
        logger.exception(
            "Database error while loading settlement information."
        )

        st.error(
            "Unable to load settlement information. "
            "Please try again later."
        )

    except Exception:

        db.rollback()
        logger.exception(
            "Unexpected error in settlement management."
        )

        st.error(
            "Something went wrong while loading settlements. "
            "Please try again."
        )

    finally:
        db.close()
