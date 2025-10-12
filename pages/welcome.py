import streamlit as st
from utils.process_locator import save_current_page, Page, run_redirect
from data.SelectValues import DefaultUseCases
from utils.utils import JSON_SELECTED_USE_CASE_PATH
import json
import os

run_redirect(Page.WELCOME.value)

st.header("Welcome to Project METIS")

st.write("Explanation about the project...")

st.write("---")
st.warning("If you want to enter your Tool Stack and Manual Tasks to get recommendations, please proceed to the next step by using the button below.")

if st.button("🛠️ Proceed to Tool Stack and Manual Tasks Entry"):
  save_current_page(Page.TOOLS)
  st.switch_page(Page.TOOLS.value)

st.write("---")
st.warning("If you want to have general recommendations without detailed input data, please choose the related option below.")

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
  default_use_case = st.selectbox("Select your Use Case", DefaultUseCases)

if st.button("💾 Save Use Case and Continue to Recommendations"):
  with open(JSON_SELECTED_USE_CASE_PATH, "w") as f:
    json.dump({"selected_use_case": default_use_case}, f)
    save_current_page(Page.READY_USE_CASE)
    st.switch_page(Page.READY_USE_CASE.value)