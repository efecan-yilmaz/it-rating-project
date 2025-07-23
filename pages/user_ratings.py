import streamlit as st
from utils.utils import JSON_DETAILS_DATA_PATH, load_details_data_from_json, TEMPLATE_PATH
import pandas as pd
import openpyxl
from io import BytesIO

st.title("User Ratings Collection")

details_df = load_details_data_from_json(JSON_DETAILS_DATA_PATH)

if details_df.empty:
    st.info("No tools added yet. Please follow previous steps to add tools to collect user ratings.")
else:
    # Load template
    wb = openpyxl.load_workbook(TEMPLATE_PATH)
    ws = wb.active

    # Fill "tool" column starting from 5A
    for idx, tool in enumerate(details_df["tool"], start=5):
        ws[f"A{idx}"] = tool

    # Fill "category" column starting from 5B
    for idx, category in enumerate(details_df["category"], start=5):
        ws[f"B{idx}"] = category

    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    st.download_button(
        label="⬇️ Download User Rating Collection Excel",
        data=output,
        file_name="user_rating_collection.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.button("📤 Upload User Rating Collection Excel")