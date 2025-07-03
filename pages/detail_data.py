import streamlit as st
import pandas as pd

from utils.utils import JSON_FILE_PATH, load_tool_data_from_json, JSON_MANUAL_TASKS_PATH, load_manual_task_data_from_json

st.title("Tool Details Collection")
st.write("Please select details for entered tools. Double click to edit the value in the column.")

# Load data
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
    processed_manual_tasks_df['category'] = manual_task_df['Manual Task']
    processed_manual_tasks_df['tool'] = 'None'
else:
    processed_manual_tasks_df = pd.DataFrame(columns=['tool', 'category'])

# Combine the two dataframes
if not processed_tools_df.empty or not processed_manual_tasks_df.empty:
    combined_df = pd.concat([processed_tools_df, processed_manual_tasks_df], ignore_index=True)

    # Add default value columns as requested
    combined_df['digitalization'] = 'Automation'  # Default for tools
    # For manual tasks (where tool is 'None'), set digitalization to 'Manual'
    combined_df.loc[combined_df['tool'] == 'None', 'digitalization'] = 'Manual'
    combined_df['ai level'] = 'No'
    combined_df['centralization'] = 'Local'
    combined_df['syncronization'] = 'API-Real-Time'
    combined_df['colloborative'] = 'Not Collaborative'

    # Fill NA in the tool column with an empty string for cleaner display
    combined_df['tool'] = combined_df['tool'].fillna('')

    # Reorder columns to the specified format
    final_df = combined_df[['category', 'tool', 'digitalization', 'ai level', 'centralization', 'syncronization', 'colloborative']]

    # Split the dataframe into tools and manual tasks for separate display
    tools_display_df = final_df[final_df['tool'] != 'None'].reset_index(drop=True)
    manual_tasks_display_df = final_df[final_df['tool'] == 'None'].reset_index(drop=True)

    # Define the common column configuration for display labels
    column_config = {
        "category": "Category",
        "tool": "Tool",
        "digitalization": "Digitalization",
        "ai level": "AI Level",
        "centralization": "Centralization",
        "syncronization": "Syncronization",
        "colloborative": "Colloborative",
    }

    # Display editable table for tools
    if not tools_display_df.empty:
        st.subheader("Tool Details")
        # Update the column config specifically for the editor's selectbox
        editor_column_config = column_config.copy()
        editor_column_config["digitalization"] = st.column_config.SelectboxColumn(
            "Digitalization",
            help="Select the digitalization level of the tool",
            options=["Automation", "AI-Assisted"],
            required=True,
        )
        editor_column_config["ai level"] = st.column_config.SelectboxColumn(
            "AI Level",
            help="Select the AI level of the tool",
            options=["No", "Descriptive"],
            required=True,
        )
        editor_column_config["centralization"] = st.column_config.SelectboxColumn(
            "Centralization",
            help="Select the centralization of the tool",
            options=["Local", "SaaS", "Cloud"],
            required=True,
        )
        editor_column_config["syncronization"] = st.column_config.SelectboxColumn(
            "Syncronization",
            help="Select the syncronization of the tool",
            options=["API-Real-Time", "No-Local-Server", "Server-Real-Time"],
            required=True,
        )
        editor_column_config["colloborative"] = st.column_config.SelectboxColumn(
            "Colloborative",
            help="Select if the tool is collaborative",
            options=["Not Collaborative", "Collaborative"],
            required=True,
        )

        st.data_editor(
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
        manual_tasks_editor_config["centralization"] = st.column_config.SelectboxColumn(
            "Centralization",
            help="Select the centralization of the manual task",
            options=["Local", "SaaS", "Cloud"],
            required=True,
        )
        manual_tasks_editor_config["syncronization"] = st.column_config.SelectboxColumn(
            "Syncronization",
            help="Select the syncronization of the manual task",
            options=["API-Real-Time", "No-Local-Server", "Server-Real-Time"],
            required=True,
        )
        manual_tasks_editor_config["colloborative"] = st.column_config.SelectboxColumn(
            "Colloborative",
            help="Select if the manual task is collaborative",
            options=["Not Collaborative", "Collaborative"],
            required=True,
        )

        st.data_editor(
            manual_tasks_display_df,
            use_container_width=True,
            column_config=manual_tasks_editor_config,
            disabled=["category", "tool", "digitalization", "ai level"],
            hide_index=True,
            key="manual_tasks_editor"
        )
else:
    st.info("No tools or manual tasks found. Please add them in Step 1 and Step 2.")
