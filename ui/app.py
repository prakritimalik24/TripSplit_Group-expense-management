
import logging
import streamlit as st

from backend.db.session import SessionLocal
from backend.services.auth_service import get_authenticated_user

from ui.auth import render_auth_page
from ui.dashboard import render_dashboard
from ui.groups import render_groups
from ui.expenses import render_expenses
from ui.settlements import render_settlements
from ui.style import apply_styles


logging.basicConfig(level=logging.INFO)


st.set_page_config(
    page_title="TripSplit",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_styles()


# ----------------------------------
# SESSION MANAGEMENT
# ----------------------------------

def clear_session():
    """Clear all Streamlit session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.session_state.user = None
    st.session_state.access_token = None


if "user" not in st.session_state:
    st.session_state.user = None

if "access_token" not in st.session_state:
    st.session_state.access_token = None


# ----------------------------------
# VERIFY JWT ON EVERY APP RERUN
# ----------------------------------

def validate_session():

    token = st.session_state.access_token

    if not token:
        if st.session_state.user is not None:
            clear_session()
        return

    db = SessionLocal()

    try:
        authenticated_user = get_authenticated_user(
            db=db,
            token=token
        )

    except Exception:
        logging.exception("Session verification failed.")

        st.error(
            "Unable to verify your session right now. "
            "Please try again later."
        )
        st.stop()

    finally:
        db.close()

    if authenticated_user is None:
        clear_session()
        st.warning(
            "Your session has expired or is invalid. Please log in again."
        )
        return

    # Always refresh user information from the database.
    # Do not trust an old user object stored in session state.
    st.session_state.user = {
        "id": str(authenticated_user.id),
        "name": authenticated_user.name,
        "email": authenticated_user.email
    }


validate_session()


# ----------------------------------
# APPLICATION
# ----------------------------------

st.title("Welcome to TripSplit")
st.caption("Split expenses. Track balances. Travel together.")
st.divider()


if st.session_state.user is None:

    render_auth_page()

else:

    with st.sidebar:

        st.subheader("TripSplit")

        st.write(
            f"Welcome {st.session_state.user['name']}!"
        )

        if st.button(
            "Logout",
            use_container_width=True
        ):

            clear_session()
            st.rerun()

    page = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Groups",
            "Expenses",
            "Settlements"
        ]
    )

    if page == "Dashboard":
        render_dashboard()

    elif page == "Groups":
        render_groups()

    elif page == "Expenses":
        render_expenses()

    elif page == "Settlements":
        render_settlements()
