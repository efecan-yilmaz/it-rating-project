import streamlit as st

st.set_page_config(layout="wide")

st.sidebar.image("assets/metis_logo.jpeg", use_container_width=True)

pages = {
    "Step 1:": [st.Page("pages/tools.py", title="IT Tool Data Collection")],
    "Step 2:": [st.Page("pages/manual_tasks.py", title="Manual Tasks Collection")],
    "Step 3:": [st.Page("pages/detail_data.py", title="Tool Details Collection")],
    "Step 4:": [st.Page("pages/user_ratings.py", title="User Ratings Collection")],
    "Step 5:": [st.Page("pages/kpi_selection.py", title="KPI Selection")],
    "Dashboard": [st.Page("pages/dashboard.py", title="Dashboard")]
}

pg = st.navigation(pages)
pg.run()