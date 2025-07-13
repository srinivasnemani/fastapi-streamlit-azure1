import streamlit as st
from src.pages import data_management, pnl_summary
from src.utils.constants import PAGE_ICON, PAGE_TITLE

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

st.markdown(
    """
<style>
    .main .block-container {
        background-color: #ffffff;
    }
    .stApp {
        background-color: #ffffff;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        margin-bottom: 0.5rem;
        text-align: left;
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        box-shadow: none;
    }
    .stButton>button:hover {
        background-color: #e2e6ea;
        border-color: #1f77b4;
    }
    .dataframe {
        background-color: #ffffff;
    }
    .element-container {
        background-color: #ffffff;
    }
</style>
""",
    unsafe_allow_html=True,
)


def main() -> None:
    st.markdown(
        '<h1 class="main-header">📈 Trade PnL Analysis</h1>', unsafe_allow_html=True
    )

    st.sidebar.title("Page Navigation")

    if "page" not in st.session_state:
        st.session_state.page = "Data Management"

    if st.sidebar.button("Data Management", use_container_width=True):
        st.session_state.page = "Data Management"
    if st.sidebar.button("PnL Summary", use_container_width=True):
        st.session_state.page = "PnL Summary"

    if st.session_state.page == "Data Management":
        data_management.show()
    elif st.session_state.page == "PnL Summary":
        pnl_summary.show()


if __name__ == "__main__":
    main()
