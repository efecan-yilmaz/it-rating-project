import streamlit as st
from utils.utils import reset_application_data

st.title("Settings Page")

st.warning("Reset application. This will delete all the data collected and restart the application to its initial state.")

if st.button("🗑️ Reset Application"):
    reset_application_data()
    st.success("Application has been reset. Please go to the welcome page to start over.")