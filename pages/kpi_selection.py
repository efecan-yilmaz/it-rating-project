import streamlit as st
import pandas as pd
import random
import os

from utils.utils import (
    load_tool_data_from_json,
    JSON_MANUAL_TASKS_PATH,
    load_manual_task_data_from_json,
    JSON_DETAILS_DATA_PATH,
    JSON_KPI_DETAILS_DATA_PATH,
    load_details_data_from_json,
    export_data_to_json
)
    
from data.SelectValues import (
    DigitalizationOptions,
    AILevelOptions,
    synchronizationOptions,
    ColloborativeOptions,
    NeedForChangeOptions
)

st.title("KPI Selection")
st.write("Please mark your KPIs for the tools and manual tasks you have entered.")
st.write("Please asign them relevant 'Need for Change' values.")
st.write("You can also change the values of the tools and manual tasks you have entered in the previous steps to emphasize what you expect them in the future.")

def generate_random_scores(length):
    return [round(random.uniform(1, 5), 1) for _ in range(length)]

# Load data
details_df = load_details_data_from_json(JSON_DETAILS_DATA_PATH)

# --- Synchronize KPI details with details data ---
if os.path.exists(JSON_KPI_DETAILS_DATA_PATH):
    kpi_details_df = load_details_data_from_json(JSON_KPI_DETAILS_DATA_PATH)
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
        new_entries['setAsKpi'] = False
        new_entries['needForChange'] = "Won't"
        new_entries['qualityScore'] = generate_random_scores(len(new_entries))
        new_entries['usageScore'] = generate_random_scores(len(new_entries))
        new_entries['timeScore'] = generate_random_scores(len(new_entries))
        merged = pd.concat([merged, new_entries], ignore_index=True)
else:
    # If KPI details file doesn't exist, use all details data with default values
    merged = details_df.copy()
    merged['setAsKpi'] = False
    merged['needForChange'] = "Won't"
    merged['qualityScore'] = generate_random_scores(len(merged))
    merged['usageScore'] = generate_random_scores(len(merged))
    merged['timeScore'] = generate_random_scores(len(merged))

# Save merged to file and session state for editing
st.session_state['kpi_details_df'] = merged
export_data_to_json(merged, JSON_KPI_DETAILS_DATA_PATH)

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
        "category": "Collaborative Activities",
        "tool": "Tool",
        "digitalization": "Digitalization",
        "aiLevel": "AI Level",
        "synchronization": "synchronization",
        "colloborative": "Colloborative",
        "setAsKpi": st.column_config.CheckboxColumn(label="Set As KPI", default=False),
        "needForChange": st.column_config.SelectboxColumn(label="Need For Change", options=NeedForChangeOptions),
        "qualityScore": st.column_config.NumberColumn(label="Quality Score", format="%.1f", min_value=1.0, max_value=5.0),
        "usageScore": st.column_config.NumberColumn(label="Usage Score", format="%.1f", min_value=1.0, max_value=5.0),
        "timeScore": st.column_config.NumberColumn(label="Time Score", format="%.1f", min_value=1.0, max_value=5.0),
    }

    # Display editable table for tools
    if not edited_tools_df.empty:
        st.subheader("Tool Details")
        tools_display_cols = [
            'setAsKpi', 'needForChange', 'qualityScore', 'usageScore', 'timeScore',
            'category', 'tool', 'digitalization', 'aiLevel', 'synchronization', 'colloborative'
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
            "synchronization",
            help="Select the synchronization of the tool",
            options=synchronizationOptions,
            required=True,
        )
        editor_column_config["colloborative"] = st.column_config.SelectboxColumn(
            "Colloborative",
            help="Select if the tool is collaborative",
            options=ColloborativeOptions,
            required=True,
        )

        edited_tools_df = st.data_editor(
            edited_tools_df,
            use_container_width=True,
            column_config=editor_column_config,
            disabled=["category", "tool", "timeScore", "qualityScore", "usageScore"],
            hide_index=True,
            key="tool_details_editor"
        )

    # Display editable table for manual tasks
    if not edited_manual_tasks_df.empty:
        st.subheader("Manual Tasks")
        manual_tasks_display_cols = [
            'setAsKpi', 'needForChange', 'qualityScore', 'usageScore', 'timeScore',
            'category', 'tool', 'digitalization', 'aiLevel', 'synchronization', 'colloborative'
        ]
        edited_manual_tasks_df = edited_manual_tasks_df[manual_tasks_display_cols]

        manual_tasks_editor_config = column_config.copy()
        manual_tasks_editor_config["synchronization"] = st.column_config.SelectboxColumn(
            "synchronization",
            help="Select the synchronization of the manual task",
            options=synchronizationOptions,
            required=True,
        )
        manual_tasks_editor_config["colloborative"] = st.column_config.SelectboxColumn(
            "Colloborative",
            help="Select if the manual task is collaborative",
            options=ColloborativeOptions,
            required=True,
        )

        edited_manual_tasks_df = st.data_editor(
            edited_manual_tasks_df,
            use_container_width=True,
            column_config=manual_tasks_editor_config,
            disabled=["category", "tool", "digitalization", "aiLevel", "timeScore", "qualityScore", "usageScore"],
            hide_index=True,
            key="manual_tasks_editor"
        )

    # Only save to session_state and file when button is clicked
    if save_clicked:
        st.session_state['edited_tools_df'] = edited_tools_df
        st.session_state['edited_manual_tasks_df'] = edited_manual_tasks_df
        df_to_save = pd.concat([edited_tools_df, edited_manual_tasks_df], ignore_index=True)
        columns_to_save = ['setAsKpi', 'needForChange', 'qualityScore', 'usageScore', 'timeScore', 'category', 'tool', 'digitalization', 'aiLevel', 'synchronization', 'colloborative']
        df_to_save = df_to_save[columns_to_save]
        export_data_to_json(df_to_save, JSON_KPI_DETAILS_DATA_PATH)
        st.toast("Changes saved successfully!", icon="💾")

else:
    st.info("No details data available. Please complete the previous steps first.")

