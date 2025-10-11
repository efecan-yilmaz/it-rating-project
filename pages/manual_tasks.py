import streamlit as st
import pandas as pd
import uuid
import os
from utils.utils import JSON_MANUAL_TASKS_PATH, load_manual_task_data_from_json, export_data_to_json, JSON_DETAILS_DATA_PATH, load_details_data_from_json, JSON_FILE_PATH, load_tool_data_from_json
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

next_step_enabled = os.path.exists(JSON_MANUAL_TASKS_PATH) or os.path.exists(JSON_FILE_PATH)
if not next_step_enabled:
    st.warning("Please either enter your Manual Tasks in this step or your Tool Stack in previous step to be able to continue to next step.")
    st.warning("If you want to have general recommendations without detailed input data, please choose the related option in Welcome Page.")

col_prev_next = st.columns([0.5, 0.5])
with col_prev_next[0]:
    if st.button("⬅️ Previous step"):
        save_current_page(Page.TOOLS)
        clean_for_previous_direction(Page.MANUAL_TASKS)
        st.switch_page(Page.TOOLS.value)
with col_prev_next[1]:
    if st.button("➡️ Next step", disabled=not next_step_enabled):
        if  os.path.exists(JSON_DETAILS_DATA_PATH):
            os.remove(JSON_DETAILS_DATA_PATH)
        
        ## step for details data is cancelled
        ## going directly to user ratings step
        ## create the same file like details data to support the flow

        # Load data
        details_df = load_details_data_from_json(JSON_DETAILS_DATA_PATH)
        tool_df = load_tool_data_from_json(JSON_FILE_PATH)
        manual_task_df = load_manual_task_data_from_json(JSON_MANUAL_TASKS_PATH)

        if not tool_df.empty:
            # Reshape the dataframe from wide to long format, creating a row for each tool/category-list pair
            melted_df = pd.melt(
                tool_df,
                id_vars=['Tool Name', 'ID'],
                value_vars=['Category1', 'Category2', 'Category3', 'Category4'],
                value_name='category'
            )

            # Explode the lists in the 'category' column to create a row for each individual category item
            exploded_df = melted_df.explode('category')

            # Select and rename columns
            processed_tools_df = exploded_df[['Tool Name', 'category', 'ID']].rename(
                columns={'Tool Name': 'tool', 'ID': 'base_tool_id'}
            )

            # Remove rows where category might be an empty string or NaN
            processed_tools_df.dropna(subset=['category'], inplace=True)
            processed_tools_df = processed_tools_df[processed_tools_df['category'] != '']
            processed_tools_df['isManual'] = False
        else:
            processed_tools_df = pd.DataFrame(columns=['tool', 'category', 'base_tool_id'])

        if not manual_task_df.empty:
            # For manual tasks, the task name becomes the category, and the tool is 'None'.
            processed_manual_tasks_df = pd.DataFrame()
            processed_manual_tasks_df['category'] = manual_task_df['CategoryName']
            processed_manual_tasks_df['tool'] = 'None'
            processed_manual_tasks_df['base_tool_id'] = manual_task_df['ID']
            processed_manual_tasks_df['isManual'] = True
        else:
            processed_manual_tasks_df = pd.DataFrame(columns=['tool', 'category', 'base_tool_id'])

        # Combine the two dataframes
        if not processed_tools_df.empty or not processed_manual_tasks_df.empty:
            combined_df = pd.concat([processed_tools_df, processed_manual_tasks_df], ignore_index=True)

            # Add unique IDs for each record
            combined_df['id'] = [str(uuid.uuid4()) for _ in range(len(combined_df))]

            combined_df['digitalization'] = 'Automated'  # Default for tools
            combined_df.loc[combined_df['tool'] == 'None', 'digitalization'] = 'Manual'
            combined_df['aiLevel'] = 'No'
            combined_df['synchronization'] = 'Ad-Hoc File Sharing'
            combined_df['colloborative'] = 'Not Collaborative'
            combined_df['paymentMethod'] = 'Licensed'
            combined_df['tool'] = combined_df['tool'].fillna('')

            final_df = combined_df[['id', 'category', 'tool', 'base_tool_id', 'digitalization', 'aiLevel', 'synchronization', 'colloborative', 'paymentMethod', 'isManual']]

            details_from_disk = details_df.copy()

            # Merge with existing details data if it exists
            if not details_from_disk.empty:
                final_df.set_index(['category', 'tool'], inplace=True)
                details_from_disk.set_index(['category', 'tool'], inplace=True)
                final_df.update(details_from_disk)
                final_df.reset_index(inplace=True)

            cols = sorted(final_df.columns.tolist())
            final_df_sorted = final_df[cols].sort_values(by=['category', 'tool']).reset_index(drop=True)
            details_df_sorted = details_df[cols].sort_values(by=['category', 'tool']).reset_index(drop=True) if not details_df.empty else pd.DataFrame(columns=cols)

            if not final_df_sorted.equals(details_df_sorted):
                export_data_to_json(final_df, JSON_DETAILS_DATA_PATH)

            # df_to_save = pd.concat([edited_tools_with_id, edited_manual_tasks_with_id], ignore_index=True)
            # columns_to_save = ['id', 'category', 'tool', 'base_tool_id', 'digitalization', 'aiLevel', 'synchronization', 'colloborative', "paymentMethod"]
            # df_to_save = df_to_save[columns_to_save]
            # export_data_to_json(df_to_save, JSON_DETAILS_DATA_PATH)

        save_current_page(Page.USER_RATINGS)
        st.switch_page(Page.USER_RATINGS.value)
