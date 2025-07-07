import streamlit as st
import pandas as pd
from utils.utils import JSON_DETAILS_DATA_PATH, load_details_data_from_json

st.title("Updated Tool Stack")
st.write("Please enter your updated tool stack information below")

############ UNDER CONSTRUCTION ############
############ CODE IS WRONG ############
# Load data
details_df = load_details_data_from_json(JSON_DETAILS_DATA_PATH)

col1, col2, col3, col4 = st.columns([1,1,1, 5])
col1.button("💾 Save Changes", type="primary", use_container_width=True)
col2.button("➕ Add", type="secondary", use_container_width=True)
col3.button("🗑️ Delete", type="secondary", use_container_width=True)

if not details_df.empty:
    # Add 'Set as KPI' column with default value False
    details_df.insert(0, 'Set as KPI', False)

    # Display editable table
    edited_df = st.data_editor(
        details_df,
        use_container_width=True,
        column_config={
            "Set as KPI": st.column_config.CheckboxColumn(
                required=True
            ),
            "category": "Collaborative Activities",
            "tool": "Tool",
            "digitalization": "Digitalization",
            "aiLevel": "AI Level",
            "synchronization": "Synchronization",
            "colloborative": "Collaborative",
            "paymentMethod": "Payment Method"
        },
        hide_index=True,
        key="updated_tool_stack_editor"
    )
else:
    st.info("No tool details found. Please complete the previous steps first.")
