import streamlit as st
import pandas as pd
from utils.utils import JSON_MANUAL_TASKS_PATH, load_manual_task_data_from_json, export_data_to_json

# Initialize the DataFrame in session state if it doesn't exist
if 'manual_task_df' not in st.session_state:
    st.session_state.manual_task_df = load_manual_task_data_from_json(JSON_MANUAL_TASKS_PATH)

if "manual_task_input" not in st.session_state:
    st.session_state.manual_task_input = ""

st.title("Manual Tasks Data Collection")
st.write("Please enter your manual tasks related to IT opearations")

def add_manual_task_callback():
    manual_task = st.session_state.manual_task_input

    if manual_task:
        new_row = {
            "Manual Task": manual_task
        }
        new_row_df = pd.DataFrame([new_row])
        st.session_state.manual_task_df = pd.concat([st.session_state.manual_task_df, new_row_df], ignore_index=True)
        export_data_to_json(st.session_state.manual_task_df, JSON_MANUAL_TASKS_PATH)
        st.toast(f"Manual task '{manual_task}' added successfully!")
        st.session_state.manual_task_input = ""
    else:
        st.toast("Manual task name cannot be empty.")

st.header("New Data")

st.markdown("""
    <style>
        div[data-testid="stHint"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
col1, col2 = st.columns([4, 1])
col1.text_input("Manual Task name", key="manual_task_input", placeholder="Enter a manual task...", label_visibility="collapsed")
col2.button("➕ Add", on_click=add_manual_task_callback, use_container_width=True)

st.header("Manual Task List")

def on_table_selection(): () # necessary for dataframe to show the line selection

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
        use_container_width=True
    )