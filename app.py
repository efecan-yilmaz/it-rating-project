import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

pages = {
    "Step 1:": [st.Page("pages/tools.py", title="IT Tool Data Collection")],
    "Step 2:": [st.Page("pages/manual_tasks.py", title="Manual Tasks Collection")],
    "Step 3:": [st.Page("pages/user_ratings.py", title="User Ratings Collection")]
}

pg = st.navigation(pages)
pg.run()