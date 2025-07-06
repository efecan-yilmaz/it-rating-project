import streamlit as st
import pandas as pd
from utils.utils import JSON_MANUAL_TASKS_PATH, load_manual_task_data_from_json, export_data_to_json

CATEGORY_OPTIONS = {
    "Communication": [
        "Text chatting", "Conducting Video calls/conferencing", "Sharing - Calendars", "Sharing - Screens",
        "Sharing - Locations", "Sending Email", "Commenting on Artefacts", "Providing Status updates"
    ],
    "Data- & Knowledge Management": [
        "Searching - (Filtering) Information", "Curating and Organizing Content", "Sharing - Branch Data", "User Profile",
        "Categorizing and Tagging - Data/Information/Knowledge", "Synchronous, simultaneous editing", "Versioning Data",
        "Transforming Data", "Archiving Data", "Back Up Data", "Using Forums/discussion boards", "Submitting Ideas",
        "Rating - Ideas", "Categorizing and Tagging - Ideas", "Tracking Idea Progress", "Customizing Idea Management Workflow",
        "Creating multiple Projects", "Brainstorming Ideas", "Allocating product data (CAE data etc.)",
        "Allocating Bill of Materials (BoM)", "Managing Productworkflow and Processes",
        "Versioning and change tracking for technical documents and product data", "Establishing common language (Glossar tc.)",
        "Establishing Q&A document", "API Access", "Online Access", "Assigning access rights", "Authentification"
    ],
    "Project Management": [
        "Informing about Leave and Absences", "Delegating Tasks and Follow-up Tracking", "Assining Resources",
        "Reviewing - tasks", "Working in multiple Projects", "Planning and Scheduling Changes", "Collecting Feedback",
        "Data analysis - impact analysis", "Visualizing Data", "Sharing - Report", "Conducting Surveys and Polls",
        "Searching (Filtering) Information- Query", "Data analysis", "Data modelling", "Reporting - Problem (Ticket System, etc)",
        "Reporting - via dashboards"
    ],
    "Product Design": [
        "Developing solution options", "Rating - solution options", "Assess feasibility", "Sharing - Designs",
        "Performing numerical analysis", "Designing - 3D Modells and Assemblies", "Rendering and Visualizing Products",
        "Simulating Designs", "Preparing Prototypes", "Integrating Designs with Manufacturing Processes", "Using AR/VR environments",
        "Customizing User Interface and Ease of Use", "Gathering and defining requirements", "Negotiate product development contract",
        "Prioritising requirements", "Tracing requirements", "Validating requirements (Align results with stakeholders)",
        "Writing Lasten-/Pflichtenheft", "Create system architecture", "Open and view Designs", "Providing Feedback",
        "Review - Status Updates (Approval, Revision…)", "Designing - 2D Models and Assemblies"
    ]
}

# Initialize the DataFrame in session state if it doesn't exist
if 'manual_task_df' not in st.session_state:
    st.session_state.manual_task_df = load_manual_task_data_from_json(JSON_MANUAL_TASKS_PATH)

# Initialize category selections in session state
for cat in CATEGORY_OPTIONS:
    if cat not in st.session_state:
        st.session_state[cat] = []

st.title("Manual Tasks Data Collection")
st.write("Please select categories related to your manual IT tasks")

st.header("New Data")

def add_manual_task_callback():
    new_rows = []
    existing = st.session_state.manual_task_df

    for group, options in CATEGORY_OPTIONS.items():
        for selected in st.session_state[group]:
            # Check for duplicates
            is_duplicate = (
                not existing[
                    (existing["CategoryGroup"] == group) &
                    (existing["CategoryName"] == selected)
                ].empty
            )
            if not is_duplicate:
                new_rows.append({"CategoryGroup": group, "CategoryName": selected})

    if new_rows:
        new_row_df = pd.DataFrame(new_rows)
        st.session_state.manual_task_df = pd.concat([st.session_state.manual_task_df, new_row_df], ignore_index=True)
        export_data_to_json(st.session_state.manual_task_df, JSON_MANUAL_TASKS_PATH)
        st.toast("Manual task categories added successfully!")
        for cat in CATEGORY_OPTIONS:
            st.session_state[cat] = []
    else:
        st.toast("No new categories to add (duplicates are not allowed).")

col1, col2, col3, col4 = st.columns(4)
col1.multiselect("Communication", CATEGORY_OPTIONS["Communication"], key="Communication")
col2.multiselect("Data- & Knowledge Management", CATEGORY_OPTIONS["Data- & Knowledge Management"], key="Data- & Knowledge Management")
col3.multiselect("Project Management", CATEGORY_OPTIONS["Project Management"], key="Project Management")
col4.multiselect("Product Design", CATEGORY_OPTIONS["Product Design"], key="Product Design")

cols = st.columns([0.1, 0.9])  # First column is much smaller
with cols[0]:
    st.button("➕ Add", on_click=add_manual_task_callback, use_container_width=True)

st.header("Manual Task List")

def on_table_selection(): ()

def delete_from_table():
    current_df = st.session_state.manual_task_df
    st.session_state.manual_task_df = current_df.drop(st.session_state.manual_task_df_edit.selection.rows).reset_index(drop=True)
    export_data_to_json(st.session_state.manual_task_df, JSON_MANUAL_TASKS_PATH)
    st.toast("Selected task(s) deleted.")

if st.session_state.manual_task_df.empty:
    st.info("No manual tasks added yet. Use the form above to add your first task.")
else:
    st.button("🗑️ Delete Selected", on_click=delete_from_table)
    st.dataframe(
        st.session_state.manual_task_df,
        selection_mode="multi-row",
        on_select=on_table_selection,
        key="manual_task_df_edit",
        column_config={
            "CategoryGroup": "Category Group",
            "CategoryName": "Category Name",
        },
        use_container_width=True
    )