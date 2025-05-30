import streamlit as st
from utils.utils import JSON_FILE_PATH, load_tool_data_from_json

st.title("User Ratings Collection")

# Initialize the DataFrame in session state if it doesn't exist
if 'tool_data_df' not in st.session_state:
    st.session_state.tool_data_df = load_tool_data_from_json(JSON_FILE_PATH)


if st.session_state.tool_data_df.empty:
    st.info("No tools added yet. Use Step 1: IT Tool Data Collection page to add your IT tools.")
else:
	st.button("✨ Generate User Rating Collection Excel")
	st.button("📤 Upload User Rating Collection Excel")