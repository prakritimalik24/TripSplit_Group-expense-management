
import logging
import streamlit as st

from backend.db.session import SessionLocal

from backend.services.auth_service import (
    register_user,
    login_user
)


logger = logging.getLogger(__name__)


def render_auth_page():

    st.title("Welcome to TripSplit")
    st.write("Manage shared expenses with your friends.")

    login_tab, register_tab = st.tabs(
        ["Login", "Register"]
    )

    # ==================================
    # LOGIN TAB
    # ==================================

    with login_tab:

        st.subheader("Login to your account")

        with st.form("login_form"):

            email = st.text_input("Email")

            password = st.text_input(
                "Password",
                type="password"
            )

            login_button = st.form_submit_button(
                "Login"
            )

        if login_button:

            if not email.strip() or not password:
                st.warning(
                    "Please enter email and password."
                )

            else:

                db = SessionLocal()

                try:

                    result = login_user(
                        db=db,
                        email=email,
                        password=password
                    )

                    st.session_state.user = {
                        "id": str(result["user"].id),
                        "name": result["user"].name,
                        "email": result["user"].email
                    }

                    st.session_state.access_token = (
                        result["access_token"]
                    )

                    st.success("Login successful!")

                    st.rerun()

                except (ValueError, PermissionError) as error:

                    st.error(str(error))

                except Exception:

                    logger.exception(
                        "Unexpected error during login."
                    )

                    st.error(
                        "Unable to log in right now. "
                        "Please try again later."
                    )

                finally:
                    db.close()

    # ==================================
    # REGISTRATION TAB
    # ==================================

    with register_tab:

        st.subheader("Create your account")

        with st.form("register_form"):

            name = st.text_input("Full Name")

            email = st.text_input(
                "Email",
                key="register_email"
            )

            password = st.text_input(
                "Password",
                type="password",
                key="register_password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            register_button = st.form_submit_button(
                "Create Account"
            )

        if register_button:

            if not name.strip() or not email.strip() or not password:
                st.warning(
                    "Please fill all required fields."
                )

            elif password != confirm_password:
                st.error("Passwords do not match.")

            else:

                db = SessionLocal()

                try:

                    register_user(
                        db=db,
                        name=name,
                        email=email,
                        password=password
                    )

                    st.success(
                        "Account created successfully! "
                        "Please login."
                    )

                except ValueError as error:

                    st.error(str(error))

                except Exception:

                    logger.exception(
                        "Unexpected error during registration."
                    )

                    st.error(
                        "Unable to create your account right now. "
                        "Please try again later."
                    )

                finally:
                    db.close()
