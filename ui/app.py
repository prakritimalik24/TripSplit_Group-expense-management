import sys
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).resolve().parents[1]

# Add project root to Python path
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))



import logging
import os
import time

import streamlit as st
import extra_streamlit_components as stx

from backend.db.session import SessionLocal
from backend.services.auth_service import get_authenticated_user

from ui.auth import render_auth_page
from ui.dashboard import render_dashboard
from ui.groups import render_groups
from ui.expenses import render_expenses
from ui.settlements import render_settlements
from ui.style import apply_styles


logging.basicConfig(level=logging.INFO)

COOKIE_NAME = "tripsplit_access_token"

COOKIE_SECURE = (
    os.getenv("COOKIE_SECURE", "false").lower() == "true"
)


# ----------------------------------
# PAGE CONFIGURATION
# ----------------------------------

st.set_page_config(
    page_title="TripSplit | Shared Expenses",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_styles()


# ----------------------------------
# BRANDING & TYPOGRAPHY
# ----------------------------------

st.markdown(
    """
    <style>
    /* Main headings */
    .stApp h1 {
        color: #D4A0A7 !important;
        font-weight: 750 !important;
        letter-spacing: -1.5px;
    }

    /* Section headings */
    .stApp h2 {
        color: #8CABBE !important;
        font-weight: 650 !important;
    }

    /* Smaller headings */
    .stApp h3 {
        color: #D4A0A7 !important;
        font-weight: 600 !important;
    }

    /* Captions */
    .stApp [data-testid="stCaptionContainer"] {
        color: #AAB9C5 !important;
    }

    /* Metric labels */
    [data-testid="stMetricLabel"] {
        color: #8CABBE !important;
    }

    /* Metric values */
    [data-testid="stMetricValue"] {
        color: #F5F7FA !important;
        font-weight: 700 !important;
    }

    /* Sidebar branding */
    [data-testid="stSidebar"] h2 {
        color: #D4A0A7 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ----------------------------------
# COOKIE MANAGER
# ----------------------------------

@st.fragment
def init_cookie_manager():
    return stx.CookieManager(
        key="tripsplit_cookie_manager"
    )


cookie_manager = init_cookie_manager()


# ----------------------------------
# SESSION INITIALIZATION
# ----------------------------------

if "user" not in st.session_state:
    st.session_state.user = None

if "access_token" not in st.session_state:
    st.session_state.access_token = None


# ----------------------------------
# SESSION CLEANUP
# ----------------------------------

def clear_session():

    try:
        cookie_manager.delete(
            COOKIE_NAME,
            key="delete_tripsplit_cookie"
        )

    except Exception:
        logging.exception(
            "Unable to delete authentication cookie."
        )

    st.session_state.user = None
    st.session_state.access_token = None


# ----------------------------------
# SESSION VALIDATION
# ----------------------------------

def validate_session():

    token = st.session_state.access_token

    if not token:

        try:
            cookies = cookie_manager.get_all(
                key="load_tripsplit_cookies"
            )

            token = cookies.get(COOKIE_NAME)

        except Exception:

            logging.exception(
                "Unable to retrieve browser cookies."
            )

            token = None

        if token:
            st.session_state.access_token = token

    if not token:
        st.session_state.user = None
        return

    db = SessionLocal()

    try:

        authenticated_user = get_authenticated_user(
            db=db,
            token=token
        )

    except Exception:

        logging.exception(
            "Session verification failed."
        )

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
            "Your session has expired or is invalid. "
            "Please log in again."
        )

        return

    st.session_state.user = {
        "id": str(authenticated_user.id),
        "name": authenticated_user.name,
        "email": authenticated_user.email
    }


validate_session()


# ----------------------------------
# APPLICATION BRANDING
# ----------------------------------

st.markdown(
    """
    <div style="
        color: #8CABBE;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 3px;
        margin-bottom: -12px;
    ">
        YOUR SHARED JOURNEY
    </div>
    """,
    unsafe_allow_html=True
)

st.title("TripSplit.")

st.caption(
    "Good trips. Clear tabs. Zero awkward math."
)

st.divider()


# ----------------------------------
# AUTHENTICATION PAGE
# ----------------------------------

if st.session_state.user is None:

    render_auth_page(cookie_manager)


# ----------------------------------
# AUTHENTICATED APPLICATION
# ----------------------------------

else:

    with st.sidebar:

        st.subheader("TripSplit.")

        st.caption(
            "Your travel companion"
        )

        st.write(
            f"Welcome, {st.session_state.user['name']}!"
        )

        st.divider()

        if st.button(
            "Logout",
            use_container_width=True
        ):

            clear_session()

            time.sleep(1)

            st.rerun()

    page = st.sidebar.radio(
        "Explore",
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
