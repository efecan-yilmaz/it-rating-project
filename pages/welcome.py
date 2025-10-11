import streamlit as st
from utils.process_locator import save_current_page, Page, run_redirect

run_redirect(Page.WELCOME.value)

st.header("Welcome to Project METIS")

st.write("Explanation about the project...")

st.warning("If you want to enter your Tool Stack and Manual Tasks to get recommendations, please proceed to the next step by using the button below.")

if st.button("🛠️ Proceed to Tool Stack and Manual Tasks Entry"):
  save_current_page(Page.TOOLS)
  st.switch_page(Page.TOOLS.value)

st.warning("If you want to have general recommendations without detailed input data, please choose the related option below.")