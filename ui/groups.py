
import streamlit as st
from uuid import UUID

from sqlalchemy import select

from backend.db.session import SessionLocal
from backend.models import GroupMember

from backend.services.group_service import (
    create_group,
    get_all_groups,
    get_group_by_id
)

from backend.services.invitation_service import (
    create_invitation,
    accept_invitation
)


def render_groups():

    user_id = UUID(st.session_state.user["id"])

    st.title("👥 Group Management")
    st.caption("Create groups, manage members and invite friends.")

    create_tab, my_groups_tab, join_tab = st.tabs(
        ["Create Group", "My Groups", "Join Group"]
    )

    # --------------------------------
    # 1. CREATE GROUP
    # --------------------------------

    with create_tab:

        st.subheader("Create a New Group")

        with st.form("create_group_form"):

            group_name = st.text_input("Group Name")

            description = st.text_area(
                "Description",
                placeholder="E.g. Goa Trip 2026"
            )

            create_button = st.form_submit_button(
                "Create Group",
                use_container_width=True
            )

        if create_button:

            if not group_name.strip():
                st.warning("Please enter a group name.")

            else:

                db = SessionLocal()

                try:
                    group = create_group(
                        db=db,
                        name=group_name.strip(),
                        description=description.strip() or None,
                        created_by=user_id
                    )

                    st.success(
                        f"Group '{group.name}' created successfully!"
                    )
                    st.info("You have been added as the group admin.")

                except Exception as error:
                    st.error(f"Unable to create group: {error}")

                finally:
                    db.close()

    # --------------------------------
    # 2. MY GROUPS
    # --------------------------------

    with my_groups_tab:

        st.subheader("Your Groups")

        db = SessionLocal()

        try:
            groups = get_all_groups(
                db=db,
                user_id=user_id
            )

            if not groups:

                st.info(
                    "You haven't joined any groups yet. "
                    "Create a group to get started!"
                )

            else:

                selected_group = st.selectbox(
                    "Select a group",
                    options=groups,
                    format_func=lambda group: group.name,
                    key="selected_group"
                )

                if selected_group:

                    group = get_group_by_id(
                        db=db,
                        group_id=selected_group.id,
                        user_id=user_id
                    )

                    if group:

                        st.divider()

                        st.subheader(f"📁 {group.name}")

                        st.write(
                            group.description or "No description available."
                        )

                        st.caption(f"Status: {group.status}")

                        # Fetch group members
                        members = db.execute(
                            select(GroupMember).where(
                                GroupMember.group_id == group.id
                            )
                        ).scalars().all()

                        st.subheader("Group Members")

                        st.metric("Total Members", len(members))

                        for member in members:

                            member_name = member.user.name

                            if member.role == "admin":
                                st.write(
                                    f"👑 **{member_name}** — Admin"
                                )
                            else:
                                st.write(
                                    f"👤 {member_name} — Member"
                                )

                        # Check current user's role
                        current_membership = next(
                            (
                                member for member in members
                                if member.user_id == user_id
                            ),
                            None
                        )

                        if current_membership and current_membership.role == "admin":

                            st.divider()
                            st.subheader("Invite Friends")

                            if st.button(
                                "Generate Invitation",
                                key=f"invite_{group.id}"
                            ):

                                invitation = create_invitation(
                                    db=db,
                                    group_id=group.id,
                                    invited_by=user_id
                                )

                                st.session_state[
                                    f"invite_token_{group.id}"
                                ] = invitation["token"]

                            token = st.session_state.get(
                                f"invite_token_{group.id}"
                            )

                            if token:

                                st.success("Invitation generated!")
                                st.write("Share this token with your friend:")
                                st.code(token)

                                st.caption(
                                    "This invitation expires after 7 days. "
                                    "The token can be used only once."
                                )

        except Exception as error:
            st.error(f"Unable to load groups: {error}")

        finally:
            db.close()

    # --------------------------------
    # 3. JOIN GROUP
    # --------------------------------

    with join_tab:

        st.subheader("Join an Existing Group")

        st.write(
            "Enter the invitation token shared by your group admin."
        )

        with st.form("join_group_form"):

            invitation_token = st.text_input(
                "Invitation Token"
            )

            join_button = st.form_submit_button(
                "Join Group",
                use_container_width=True
            )

        if join_button:

            if not invitation_token.strip():

                st.warning("Please enter an invitation token.")

            else:

                db = SessionLocal()

                try:
                    membership = accept_invitation(
                        db=db,
                        token=invitation_token.strip(),
                        user_id=user_id
                    )

                    st.success(
                        "You have successfully joined the group!"
                    )

                    st.write(f"Group ID: {membership.group_id}")

                except (ValueError, PermissionError) as error:
                    st.error(str(error))

                except Exception as error:
                    st.error(f"Unable to join group: {error}")

                finally:
                    db.close()
