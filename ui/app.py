import streamlit as st
from ui.auth import render_auth_page
from ui.dashboard import render_dashboard

st.set_page_config(
    page_title = "TripSplit",
    layout = "wide",
    initial_sidebar_state="expanded"
)

if "user" not in st.session_state:
    st.session_state.user = None

if "access_token" not in st.session_state:
    st.session_state.access_token = None


st.title("Welcome to TripSplit")

st.caption("Split expenses. Track balances . Travel together")

st.divider()

if st.session_state.user is None:
    render_auth_page()
else:

    with st.sidebar:
        st.subheader("TripSplit")
        st.write(f"Welcome {st.session_state.user['name']}!")

        if st.button("Logout", use_container_width=True):

            st.session_state.user = None
            st.session_state.access_token = None

            st.rerun()

    render_dashboard()
