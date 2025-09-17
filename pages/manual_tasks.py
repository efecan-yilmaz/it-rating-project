import streamlit as st
import pandas as pd
import uuid
import os
from utils.utils import JSON_MANUAL_TASKS_PATH, load_manual_task_data_from_json, export_data_to_json
from data.SelectValues import (Category1Options, Category2Options, Category3Options, Category4Options)
from utils.process_locator import determine_page, save_current_page, Page, run_redirect, clean_for_previous_direction

run_redirect(Page.MANUAL_TASKS.value)

CATEGORY_OPTIONS = {
    "Communication": sorted(Category1Options),
    "Data- & Knowledge Management": sorted(Category2Options),
    "Project Management": sorted(Category3Options),
    "Product Design": sorted(Category4Options)
}

# Initialize the DataFrame in session state if it doesn't exist
if 'manual_task_df' not in st.session_state or not os.path.exists(JSON_MANUAL_TASKS_PATH):
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
                new_rows.append({
                    "ID": str(uuid.uuid4()),
                    "CategoryGroup": group,
                    "CategoryName": selected
                })

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
        st.session_state.manual_task_df[["CategoryGroup", "CategoryName"]],
        selection_mode="multi-row",
        on_select=on_table_selection,
        key="manual_task_df_edit",
        column_config={
            "CategoryGroup": "Category Group",
            "CategoryName": "Category Name",
        },
        use_container_width=True
    )

next_step_enabled = os.path.exists(JSON_MANUAL_TASKS_PATH)
if not next_step_enabled:
    st.warning("Please complete Manual Tasks Data Collection before proceeding to the next step.")

col_prev_next = st.columns([0.5, 0.5])
with col_prev_next[0]:
    if st.button("⬅️ Previous step"):
        save_current_page(Page.TOOLS)
        clean_for_previous_direction(Page.MANUAL_TASKS)
        st.switch_page(Page.TOOLS.value)
with col_prev_next[1]:
    if st.button("➡️ Next step", disabled=not next_step_enabled):
        save_current_page(Page.DETAIL_DATA)
        st.switch_page(Page.DETAIL_DATA.value)
