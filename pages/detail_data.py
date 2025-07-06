import streamlit as st
import pandas as pd

from utils.utils import (
    JSON_FILE_PATH,
    load_tool_data_from_json,
    JSON_MANUAL_TASKS_PATH,
    load_manual_task_data_from_json,
    JSON_DETAILS_DATA_PATH,
    load_details_data_from_json,
    export_data_to_json
)

from data.SelectValues import (
    DigitalizationOptions,
    AILevelOptions,
    synchronizationOptions,
    ColloborativeOptions
)

st.title("Tool Details Collection")
st.write("Please select details for entered tools. Double click to edit the value in the column.")

# Load data
details_df = load_details_data_from_json(JSON_DETAILS_DATA_PATH)
tool_df = load_tool_data_from_json(JSON_FILE_PATH)
manual_task_df = load_manual_task_data_from_json(JSON_MANUAL_TASKS_PATH)

if not tool_df.empty:
    # Reshape the dataframe from wide to long format, creating a row for each tool/category-list pair
    melted_df = pd.melt(
        tool_df,
        id_vars=['Tool Name'],
        value_vars=['Category1', 'Category2', 'Category3', 'Category4'],
        value_name='category'
    )

    # Explode the lists in the 'category' column to create a row for each individual category item
    exploded_df = melted_df.explode('category')

    # Select and rename columns
    processed_tools_df = exploded_df[['Tool Name', 'category']].rename(columns={'Tool Name': 'tool'})

    # Remove rows where category might be an empty string or NaN
    processed_tools_df.dropna(subset=['category'], inplace=True)
    processed_tools_df = processed_tools_df[processed_tools_df['category'] != '']
else:
    processed_tools_df = pd.DataFrame(columns=['tool', 'category'])

if not manual_task_df.empty:
    # For manual tasks, the task name becomes the category, and the tool is 'None'.
    processed_manual_tasks_df = pd.DataFrame()
    processed_manual_tasks_df['category'] = manual_task_df['CategoryName']
    processed_manual_tasks_df['tool'] = 'None'
else:
    processed_manual_tasks_df = pd.DataFrame(columns=['tool', 'category'])

# Combine the two dataframes
if not processed_tools_df.empty or not processed_manual_tasks_df.empty:
    combined_df = pd.concat([processed_tools_df, processed_manual_tasks_df], ignore_index=True)

    combined_df['digitalization'] = 'Automated'  # Default for tools
    # For manual tasks (where tool is 'None'), set digitalization to 'Manual'
    combined_df.loc[combined_df['tool'] == 'None', 'digitalization'] = 'Manual'
    combined_df['aiLevel'] = 'No'
    combined_df['synchronization'] = 'Ad-Hoc File Sharing'
    combined_df['colloborative'] = 'Not Collaborative'

    combined_df['tool'] = combined_df['tool'].fillna('')

    final_df = combined_df[['category', 'tool', 'digitalization', 'aiLevel', 'synchronization', 'colloborative']]

    details_from_disk = details_df.copy()

    # Merge with existing details data if it exists
    if not details_from_disk.empty:
        # Use category and tool as index for easy updating
        final_df.set_index(['category', 'tool'], inplace=True)
        # Ensure the loaded details_df has the same index
        details_from_disk.set_index(['category', 'tool'], inplace=True)
        # Update final_df with the values from details_df
        final_df.update(details_from_disk)
        # Reset index to get columns back
        final_df.reset_index(inplace=True)

    # On first load, check if the generated data (with merged details) is different
    # from what's on disk. If so, save it to sync new/deleted tools. This happens
    # silently to ensure the details file is always up-to-date.
    cols = sorted(final_df.columns.tolist())
    final_df_sorted = final_df[cols].sort_values(by=['category', 'tool']).reset_index(drop=True)
    details_df_sorted = details_df[cols].sort_values(by=['category', 'tool']).reset_index(drop=True) if not details_df.empty else pd.DataFrame(columns=cols)

    if not final_df_sorted.equals(details_df_sorted):
        export_data_to_json(final_df, JSON_DETAILS_DATA_PATH)

    # Split the dataframe into tools and manual tasks for separate display
    tools_display_df = final_df[final_df['tool'] != 'None'].reset_index(drop=True)
    manual_tasks_display_df = final_df[final_df['tool'] == 'None'].reset_index(drop=True)

    column_config = {
        "category": "Collaborative Activities",
        "tool": "Tool",
        "digitalization": "Digitalization",
        "aiLevel": "AI Level",
        "synchronization": "synchronization",
        "colloborative": "Colloborative",
    }

    save_clicked = st.button("💾 Save Changes", type="primary")

    # Display editable table for tools
    if not tools_display_df.empty:
        st.subheader("Tool Details")
        # Update the column config specifically for the editor's selectbox
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
            tools_display_df,
            use_container_width=True,
            column_config=editor_column_config,
            disabled=["category", "tool"], # Prevent editing of derived columns
            hide_index=True,
            key="tool_details_editor"
        )

    # Display editable table for manual tasks
    if not manual_tasks_display_df.empty:
        st.subheader("Manual Tasks")
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
            manual_tasks_display_df,
            use_container_width=True,
            column_config=manual_tasks_editor_config,
            disabled=["category", "tool", "digitalization", "aiLevel"],
            hide_index=True,
            key="manual_tasks_editor"
        )

    # Save only when the button is clicked
    if save_clicked:
        df_to_save = pd.concat([edited_tools_df, edited_manual_tasks_df], ignore_index=True)
        columns_to_save = ['category', 'tool', 'digitalization', 'aiLevel', 'synchronization', 'colloborative']
        df_to_save = df_to_save[columns_to_save]
        export_data_to_json(df_to_save, JSON_DETAILS_DATA_PATH)
        st.rerun()
else:
    st.info("No tools or manual tasks found. Please add them in Step 1 and Step 2.")
