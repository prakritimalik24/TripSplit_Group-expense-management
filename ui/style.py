
import streamlit as st


def apply_styles():

    st.markdown(
        """
        <style>

        /* =================================
           1. COLOR PALETTE
        ================================= */

        :root {
            --prussian-blue: #02182B;
            --pitch-black: #0F1108;
            --deep-teal: #4E6E58;
            --cool-steel: #8CABBE;
            --rosy-taupe: #D4A0A7;

            --primary-button: #355B49;
            --primary-hover: #456F59;
            --secondary-button: #456B82;
            --danger-button: #984447;
            --indigo-accent: #25283D;

            --main-text: #F5F7FA;
            --muted-text: #AAB9C5;
            --border-color: #304657;
        }


        /* =================================
           2. GLOBAL DESIGN
        ================================= */

        .stApp {
            background: var(--prussian-blue);
            color: var(--main-text);
        }

        .main .block-container {
            max-width: 1250px;
            padding: 2.5rem 2.5rem 3rem 2.5rem;
        }


        /* =================================
           3. TYPOGRAPHY
        ================================= */

        h1, h2, h3, h4 {
            color: var(--main-text) !important;
            font-weight: 650 !important;
            letter-spacing: -0.4px;
        }

        p, label, li {
            color: var(--main-text);
        }

        [data-testid="stCaptionContainer"] {
            color: var(--muted-text);
        }


        /* =================================
           4. SIDEBAR
        ================================= */

        [data-testid="stSidebar"] {
            background: var(--pitch-black);
            border-right: 1px solid var(--border-color);
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: var(--main-text);
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: var(--cool-steel) !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            color: var(--main-text) !important;
        }


        /* =================================
           5. BUTTONS
        ================================= */

        /* Primary buttons */

        .stButton > button,
        .stFormSubmitButton > button {
            background: var(--primary-button);
            color: #FFFFFF;
            border: 1px solid #527B65;
            border-radius: 9px;
            padding: 0.55rem 1.2rem;
            font-weight: 650;
            transition: all 0.2s ease;
        }

        /* Hover */

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            background: var(--primary-hover);
            color: #FFFFFF;
            border-color: var(--cool-steel);
            transform: translateY(-1px);
        }

        /* Focus */

        .stButton > button:focus,
        .stFormSubmitButton > button:focus {
            box-shadow: 0 0 0 2px var(--cool-steel);
        }

        /* Disabled */

        .stButton > button:disabled,
        .stFormSubmitButton > button:disabled {
            background: var(--indigo-accent);
            color: var(--muted-text);
            border-color: var(--indigo-accent);
            opacity: 0.7;
        }


        /* =================================
           6. INPUT FIELDS
        ================================= */

        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea,
        .stDateInput input {
            background: var(--pitch-black);
            color: var(--main-text);
            border: 1px solid var(--border-color);
            border-radius: 9px;
        }

        .stTextInput input:focus,
        .stNumberInput input:focus,
        .stTextArea textarea:focus,
        .stDateInput input:focus {
            border-color: var(--cool-steel);
            box-shadow: 0 0 0 1px var(--cool-steel);
        }

        [data-baseweb="select"] > div {
            background: var(--pitch-black);
            border-color: var(--border-color);
            border-radius: 9px;
            color: var(--main-text);
        }


        /* =================================
           7. METRIC CARDS
        ================================= */

        [data-testid="stMetric"] {
            background: var(--pitch-black);
            border: 1px solid var(--border-color);
            border-radius: 13px;
            padding: 19px;
            transition: border-color 0.2s ease;
        }

        [data-testid="stMetric"]:hover {
            border-color: var(--deep-teal);
        }

        [data-testid="stMetricLabel"] {
            color: var(--muted-text);
        }

        [data-testid="stMetricValue"] {
            color: var(--cool-steel);
            font-weight: 700;
        }


        /* =================================
           8. CONTAINERS AND EXPANDERS
        ================================= */

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--pitch-black);
            border: 1px solid var(--border-color);
            border-radius: 13px;
        }

        [data-testid="stExpander"] {
            background: var(--pitch-black);
            border: 1px solid var(--border-color);
            border-radius: 11px;
        }


        /* =================================
           9. TABS
        ================================= */

        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            border-bottom: 1px solid var(--border-color);
        }

        .stTabs [data-baseweb="tab"] {
            color: var(--muted-text);
            padding: 10px 16px;
        }

        .stTabs [aria-selected="true"] {
            color: var(--cool-steel) !important;
            border-bottom-color: var(--deep-teal) !important;
        }


        /* =================================
           10. RADIO AND CHECKBOXES
        ================================= */

        .stRadio label,
        .stCheckbox label {
            color: var(--main-text) !important;
        }


        /* =================================
           11. ALERTS AND DIVIDERS
        ================================= */

        [data-testid="stAlert"] {
            border-radius: 10px;
        }

        hr {
            border-color: var(--border-color);
        }


        /* =================================
           12. DATA TABLES
        ================================= */

        [data-testid="stDataFrame"] {
            border: 1px solid var(--border-color);
            border-radius: 10px;
            overflow: hidden;
        }


        /* =================================
           13. FORMS
        ================================= */

        [data-testid="stForm"] {
            background: var(--pitch-black);
            border: 1px solid var(--border-color);
            border-radius: 13px;
            padding: 20px;
        }


        /* =================================
           14. SCROLLBAR
        ================================= */

        ::-webkit-scrollbar {
            width: 7px;
            height: 7px;
        }

        ::-webkit-scrollbar-track {
            background: var(--prussian-blue);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--deep-teal);
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--cool-steel);
        }

        </style>
        """,
        unsafe_allow_html=True
    )
