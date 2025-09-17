import streamlit as st
import pandas as pd
import uuid
import os

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
    ColloborativeOptions,
    PaymentMethodOptions
)

from utils.process_locator import determine_page, save_current_page, Page, run_redirect, clean_for_previous_direction

run_redirect(Page.DETAIL_DATA.value)

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
else:
    processed_tools_df = pd.DataFrame(columns=['tool', 'category', 'base_tool_id'])

if not manual_task_df.empty:
    # For manual tasks, the task name becomes the category, and the tool is 'None'.
    processed_manual_tasks_df = pd.DataFrame()
    processed_manual_tasks_df['category'] = manual_task_df['CategoryName']
    processed_manual_tasks_df['tool'] = 'None'
    processed_manual_tasks_df['base_tool_id'] = manual_task_df['ID']
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

    final_df = combined_df[['id', 'category', 'tool', 'base_tool_id', 'digitalization', 'aiLevel', 'synchronization', 'colloborative', 'paymentMethod']]

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

    # Don't show 'base_tool_id' in tables
    display_columns = [c for c in final_df.columns if c not in ['id', 'base_tool_id']]
    tools_display_df = final_df[final_df['tool'] != 'None'][display_columns].reset_index(drop=True)
    manual_tasks_display_df = final_df[final_df['tool'] == 'None'][display_columns].reset_index(drop=True)

    column_config = {
        "category": "Collaborative Activities",
        "tool": "Tool",
        "digitalization": "Digitalization",
        "aiLevel": "AI Level",
        "synchronization": "synchronization",
        "colloborative": "Colloborative",
        "paymentMethod": "Payment Method"
    }

    save_clicked = st.button("💾 Save Changes", type="primary")

    # Display editable table for tools
    if not tools_display_df.empty:
        st.subheader("Tool Details")
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
        editor_column_config["paymentMethod"] = st.column_config.SelectboxColumn(
            "Payment Method",
            help="Select the payment method of the tool",
            options=PaymentMethodOptions,
            required=True,
        )

        edited_tools_df = st.data_editor(
            tools_display_df,
            use_container_width=True,
            column_config=editor_column_config,
            disabled=["category", "tool"], # "id" is not present
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
        manual_tasks_editor_config["paymentMethod"] = st.column_config.SelectboxColumn(
            "Payment Method",
            help="Select the payment method of the tool",
            options=PaymentMethodOptions,
            required=True,
        )

        edited_manual_tasks_df = st.data_editor(
            manual_tasks_display_df,
            use_container_width=True,
            column_config=manual_tasks_editor_config,
            disabled=["category", "tool", "digitalization", "aiLevel"], # "id" is not present
            hide_index=True,
            key="manual_tasks_editor"
        )

    # When saving, merge the edited data back with the original DataFrame (with 'id')
    if save_clicked:
        # Re-attach the 'id' column before saving
        # You need to match rows by 'category' and 'tool'
        def merge_with_id(edited_df, original_df):
            return pd.merge(
                original_df[['id', 'category', 'tool', 'base_tool_id']],
                edited_df,
                on=['category', 'tool'],
                how='right'
            )

        edited_tools_with_id = merge_with_id(edited_tools_df, final_df[final_df['tool'] != 'None'])
        edited_manual_tasks_with_id = merge_with_id(edited_manual_tasks_df, final_df[final_df['tool'] == 'None'])

        df_to_save = pd.concat([edited_tools_with_id, edited_manual_tasks_with_id], ignore_index=True)
        columns_to_save = ['id', 'category', 'tool', 'base_tool_id', 'digitalization', 'aiLevel', 'synchronization', 'colloborative', "paymentMethod"]
        df_to_save = df_to_save[columns_to_save]
        export_data_to_json(df_to_save, JSON_DETAILS_DATA_PATH)
        st.toast("Changes saved successfully!", icon="💾")
        st.rerun()
else:
    st.info("No tools or manual tasks found. Please add them in Step 1 and Step 2.")

next_step_enabled = os.path.exists(JSON_DETAILS_DATA_PATH)
col_prev_next = st.columns([0.5, 0.5])
with col_prev_next[0]:
    if st.button("⬅️ Previous step"):
        save_current_page(Page.MANUAL_TASKS)
        clean_for_previous_direction(Page.DETAIL_DATA)
        st.switch_page(Page.MANUAL_TASKS.value)
with col_prev_next[1]:
    if st.button("➡️ Next step", disabled=not next_step_enabled):
        save_current_page(Page.USER_RATINGS)
        st.switch_page(Page.USER_RATINGS.value)