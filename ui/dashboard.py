
import streamlit as st
from uuid import UUID

from backend.db.session import SessionLocal
from backend.services.group_service import get_all_groups


def render_dashboard():

    user = st.session_state.user

    # Welcome section
    st.title(f"Hello, {user['name']}! 👋")
    st.write("Welcome to your TripSplit dashboard.")

    st.divider()

    # Fetch user's groups
    db = SessionLocal()

    try:
        groups = get_all_groups(
            db,
            user_id=UUID(user["id"])
        )

        # Overview
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Groups", len(groups))

        with col2:
            st.metric("Account Status", "Active")

        st.divider()

        # Groups section
        st.subheader("Your Groups")

        if groups:

            for group in groups:

                with st.container(border=True):

                    st.subheader(f"📁 {group.name}")

                    if group.description:
                        st.write(group.description)
                    else:
                        st.caption("No description available.")

        else:
            st.info(
                "You haven't joined any groups yet. "
                "Create or join a group to get started!"
            )

    except Exception as error:
        st.error(f"Unable to load your groups: {error}")

    finally:
        db.close()
