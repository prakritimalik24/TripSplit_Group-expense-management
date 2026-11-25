
import logging
import os
import time
from datetime import datetime, timedelta

import streamlit as st

from backend.db.session import SessionLocal

from backend.services.auth_service import (
    register_user,
    login_user
)

from backend.security import ACCESS_TOKEN_EXPIRE_MINUTES


logger = logging.getLogger(__name__)

COOKIE_NAME = "tripsplit_access_token"

COOKIE_SECURE = (
    os.getenv("COOKIE_SECURE", "false").lower() == "true"
)


def render_auth_page(cookie_manager):

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

                    token = result["access_token"]

                    # Save authentication token in browser cookie.
                    cookie_manager.set(
                        cookie=COOKIE_NAME,
                        val=token,
                        key="save_tripsplit_login",
                        path="/",
                        expires_at=(
                            datetime.now()
                            + timedelta(
                                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                            )
                        ),
                        secure=COOKIE_SECURE,
                        same_site="strict"
                    )

                    # Store user information in Streamlit session.
                    st.session_state.user = {
                        "id": str(result["user"].id),
                        "name": result["user"].name,
                        "email": result["user"].email
                    }

                    st.session_state.access_token = token

                    st.success("Login successful!")

                    # Allow browser cookie update to complete.
                    with st.spinner("Saving your login..."):
                        time.sleep(1.5)

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
