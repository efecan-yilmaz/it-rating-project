import streamlit as st
import pandas as pd
import random
import os

from utils.utils import (
    load_tool_data_from_json,
    JSON_MANUAL_TASKS_PATH,
    load_manual_task_data_from_json,
    JSON_DETAILS_DATA_PATH,
    JSON_RE_DETAILS_DATA_PATH,
    load_details_data_from_json,
    export_data_to_json,
    JSON_USER_RATINGS_PATH
)
    
from data.SelectValues import (
    DigitalizationOptions,
    AILevelOptions,
    synchronizationOptions,
    ColloborativeOptions,
    NeedForChangeOptions
)

from utils.process_locator import determine_page, save_current_page, Page, run_redirect, clean_for_previous_direction

run_redirect(Page.REQUIREMENT_ENGINEERING.value)

st.title("Requirement Engineering")
st.write("Please asign them relevant 'Need for Change' values.")
st.write("Please assign other values for the tools to reflect your necessities.")

def calculate_voe_from_user_ratings(details_df, user_ratings_path):
    # Load user ratings
    if not os.path.exists(user_ratings_path):
        return [None] * len(details_df)
    user_ratings_df = pd.read_json(user_ratings_path)
    voe_columns = [
        "Frequency of Use", "Time Efficiency", "Output Quality",
        "Ease of Use", "Integration", "Reliability", "Satisfaction"
    ]
    # Ensure both IDs are of the same type
    details_df["id"] = details_df["id"].astype(str)
    user_ratings_df["details_id"] = user_ratings_df["details_id"].astype(str)
    # Calculate average for each details_id
    voe_map = (
        user_ratings_df.groupby("details_id")[voe_columns]
        .mean()
        .mean(axis=1)
        .to_dict()
    )
    # Map to details_df using 'id' column
    return details_df["id"].map(voe_map).round(1).fillna(3.0)

# Load data
details_df = load_details_data_from_json(JSON_DETAILS_DATA_PATH)

# --- Synchronize KPI details with details data ---
if os.path.exists(JSON_RE_DETAILS_DATA_PATH):
    kpi_details_df = load_details_data_from_json(JSON_RE_DETAILS_DATA_PATH)
    # Remove entries not in details_df
    merged = pd.merge(
        kpi_details_df,
        details_df[['category', 'tool']],
        on=['category', 'tool'],
        how='inner'
    )
    # Find new entries in details_df
    merged_keys = merged[['category', 'tool']].apply(tuple, axis=1)
    details_keys = details_df[['category', 'tool']].apply(tuple, axis=1)
    new_entries = details_df[~details_keys.isin(merged_keys)]
    # Add new entries with default values
    if not new_entries.empty:
        new_entries = new_entries.copy()
        new_entries['needForChange'] = new_entries['digitalization'].apply(lambda x: "Nice to change" if x == "Manual" else "No need to change")
        new_entries['voe'] = calculate_voe_from_user_ratings(new_entries, JSON_USER_RATINGS_PATH)
        merged = pd.concat([merged, new_entries], ignore_index=True)
else:
    # If KPI details file doesn't exist, use all details data with default values
    merged = details_df.copy()
    merged['needForChange'] = merged['digitalization'].apply(lambda x: "Nice to change" if x == "Manual" else "No need to change")
    merged['voe'] = calculate_voe_from_user_ratings(merged, JSON_USER_RATINGS_PATH)

# Save merged to file and session state for editing
st.session_state['kpi_details_df'] = merged
export_data_to_json(merged, JSON_RE_DETAILS_DATA_PATH)

# Use 'merged' as your working dataframe for KPI selection
if not merged.empty:
    # Split the dataframe into tools and manual tasks for separate display
    tools_display_df = merged[merged['tool'] != 'None'].reset_index(drop=True)
    manual_tasks_display_df = merged[merged['tool'] == 'None'].reset_index(drop=True)

    # Initialize session state for edited dataframes
    if 'edited_tools_df' not in st.session_state:
        st.session_state['edited_tools_df'] = tools_display_df.copy()

    if 'edited_manual_tasks_df' not in st.session_state:
        st.session_state['edited_manual_tasks_df'] = manual_tasks_display_df.copy()

    save_clicked = st.button("💾 Save Changes", type="primary")

    # Use local variables for editing
    edited_tools_df = st.session_state['edited_tools_df']
    edited_manual_tasks_df = st.session_state['edited_manual_tasks_df']

    column_config = {
        "category": "Activities",
        "tool": "Tool",
        "digitalization": "Digitalization",
        "aiLevel": "AI Level",
        "synchronization": "Synchronization",
        #"colloborative": "Colloborative",
        "needForChange": st.column_config.SelectboxColumn(label="Need For Change", options=NeedForChangeOptions),
        "voe": st.column_config.NumberColumn(label="VoE", format="%.1f", min_value=1.0, max_value=10),
    }

    # Display editable table for tools
    if not edited_tools_df.empty:
        st.subheader("Tool Details")
        tools_display_cols = [
            'needForChange', 'voe',
            'category', 'tool', 'digitalization', 'aiLevel', 'synchronization'#, 'colloborative'
        ]
        edited_tools_df = edited_tools_df[tools_display_cols]

        editor_column_config = column_config.copy()
        editor_column_config["digitalization"] = st.column_config.SelectboxColumn(
            "Digitalization",
            help="Select the digitalization level of the tool",
            options=DigitalizationOptions,
            required=True,
        )
        editor_column_config["aiLevel"] = st.column_config.SelectboxColumn(
            "AI Level",
            help="Select the AI level of the tool",
            options=AILevelOptions,
            required=True,
        )
        editor_column_config["synchronization"] = st.column_config.SelectboxColumn(
            "Synchronization",
            help="Select the synchronization of the tool",
            options=synchronizationOptions,
            required=True,
        )
        # editor_column_config["colloborative"] = st.column_config.SelectboxColumn(
        #     "Colloborative",
        #     help="Select if the tool is collaborative",
        #     options=ColloborativeOptions,
        #     required=True,
        # )

        edited_tools_df = st.data_editor(
            edited_tools_df,
            use_container_width=True,
            column_config=editor_column_config,
            disabled=["category", "tool", "voe"],
            hide_index=True,
            key="tool_details_editor"
        )

    # Display editable table for manual tasks
    if not edited_manual_tasks_df.empty:
        st.subheader("Manual Tasks")
        manual_tasks_display_cols = [
            'needForChange', 'voe',
            'category', 'tool', 'digitalization', 'aiLevel', 'synchronization'#, 'colloborative'
        ]
        edited_manual_tasks_df = edited_manual_tasks_df[manual_tasks_display_cols]

        manual_tasks_editor_config = column_config.copy()
        manual_tasks_editor_config["synchronization"] = st.column_config.SelectboxColumn(
            "Synchronization",
            help="Select the synchronization of the manual task",
            options=synchronizationOptions,
            required=True,
        )
        # manual_tasks_editor_config["colloborative"] = st.column_config.SelectboxColumn(
        #     "Colloborative",
        #     help="Select if the manual task is collaborative",
        #     options=ColloborativeOptions,
        #     required=True,
        # )

        edited_manual_tasks_df = st.data_editor(
            edited_manual_tasks_df,
            use_container_width=True,
            column_config=manual_tasks_editor_config,
            disabled=["category", "tool", "digitalization", "aiLevel", "voe"],
            hide_index=True,
            key="manual_tasks_editor"
        )

    # Only save to session_state and file when button is clicked
    if save_clicked:
        st.session_state['edited_tools_df'] = edited_tools_df
        st.session_state['edited_manual_tasks_df'] = edited_manual_tasks_df
        df_to_save = pd.concat([edited_tools_df, edited_manual_tasks_df], ignore_index=True)
        columns_to_save = ['needForChange', 'voe', 'category', 'tool', 'digitalization', 'aiLevel', 'synchronization']#, 'colloborative']
        df_to_save = df_to_save[columns_to_save]
        export_data_to_json(df_to_save, JSON_RE_DETAILS_DATA_PATH)
        st.toast("Changes saved successfully!", icon="💾")

else:
    st.info("No details data available. Please complete the previous steps first.")

next_step_enabled = os.path.exists(JSON_RE_DETAILS_DATA_PATH)

col_prev_next = st.columns([0.5, 0.5])
with col_prev_next[0]:
    if st.button("⬅️ Previous step"):
        save_current_page(Page.USER_RATINGS)
        clean_for_previous_direction(Page.REQUIREMENT_ENGINEERING)
        st.switch_page(Page.USER_RATINGS.value)
with col_prev_next[1]:
    if st.button("➡️ Next step", disabled=not next_step_enabled):
        save_current_page(Page.REQUIREMENT)
        st.switch_page(Page.REQUIREMENT.value)