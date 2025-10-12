import streamlit as st
from utils.process_locator import hide_hidden_header_and_list_items


st.set_page_config(layout="wide")
hide_hidden_header_and_list_items()

st.sidebar.image("assets/metis_logo.jpeg", use_container_width=True)

pages = {
    "IT Tool Data Collection:": [st.Page("pages/tools.py", title="Data Collection Process")],
    "KPIs:": [st.Page("pages/define_kpi.py", title="Define KPI"), st.Page("pages/measurement.py", title="Measurement")],
    "Data Tracking": [st.Page("pages/dashboard.py", title="Dashboard")],
    "hidden": [st.Page("pages/welcome.py", title="Welcome"), st.Page("pages/ready_use_case.py", title="Ready Use Case"), st.Page("pages/manual_tasks.py", title="Manual Tasks"), st.Page("pages/detail_data.py", title="Tool Details Collection"), st.Page("pages/user_ratings.py", title="User Ratings Collection"), st.Page("pages/requirement_engineering.py", title="Requirement Engineering"), st.Page("pages/requirement.py", title="Design Recommendation"), st.Page("pages/updated_tool_stack.py", title="Updated Tool Stack")],
}


pg = st.navigation(pages)
pg.run()
