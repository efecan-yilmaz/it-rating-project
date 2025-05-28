import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Initialize the DataFrame in session state if it doesn't exist
if 'tool_data_df' not in st.session_state:
    st.session_state.tool_data_df = pd.DataFrame(columns=["Tool Name", "Category1", "Category2", "Category3", "Category4"])

if "tool_name_input" not in st.session_state:
    st.session_state.tool_name_input = ""
if "cat1_select" not in st.session_state:
    st.session_state.cat1_select = []
if "cat2_select" not in st.session_state:
    st.session_state.cat2_select = []
if "cat3_select" not in st.session_state:
    st.session_state.cat3_select = []
if "cat4_select" not in st.session_state:
    st.session_state.cat4_select = []

st.title("Tool Collection")
st.write("Please enter your IT tools and select related catagories")

st.header("New Data")

def add_tool_callback():
    tool_name = st.session_state.tool_name_input
    category1 = st.session_state.cat1_select
    category2 = st.session_state.cat2_select
    category3 = st.session_state.cat3_select
    category4 = st.session_state.cat4_select

    if tool_name:
        new_row = {
            "Tool Name": tool_name,
            "Category1": category1,
            "Category2": category2,
            "Category3": category3,
            "Category4": category4
        }
        new_row_df = pd.DataFrame([new_row])
        st.session_state.tool_data_df = pd.concat([st.session_state.tool_data_df, new_row_df], ignore_index=True)
        st.success(f"Tool '{tool_name}' added successfully!")
        st.session_state.tool_name_input = ""
        st.session_state.cat1_select = []
        st.session_state.cat2_select = []
        st.session_state.cat3_select = []
        st.session_state.cat4_select = []
    else:
        st.error("Tool name cannot be empty.")

col1, col2, col3, col4, col5 = st.columns(5)

col1.text_input("Tool name", key="tool_name_input")
col2.multiselect("Category1", ["a", "b", "c"], key="cat1_select")
col3.multiselect("Category2", ["a", "b", "c"], key="cat2_select")
col4.multiselect("Category3", ["a", "b", "c"], key="cat3_select")
col5.multiselect("Category4", ["a", "b", "c"], key="cat4_select")

st.button("➕ Add", on_click=add_tool_callback)

st.header("Tool List")

def on_table_selection(): None # necessary for dataframe to show the line selection

def delete_from_table():
    current_df = st.session_state.tool_data_df
    st.session_state.tool_data_df = current_df.drop(st.session_state.tool_data_df_edit.selection.rows).reset_index(drop=True)

if st.session_state.tool_data_df.empty:
    st.info("No tools added yet. Use the form above to add your first tool.")
else:
    st.button("🗑️ Delete", on_click=delete_from_table)
    st.dataframe(st.session_state.tool_data_df, selection_mode="multi-row", on_select=on_table_selection, key="tool_data_df_edit")
