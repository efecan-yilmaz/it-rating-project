import streamlit as st
import pandas as pd
from data.SelectValues import UseCaseOptions, PaymentMethodOptions
from utils.utils import JSON_PRIO_DATA_PATH, export_data_to_json

st.title("Prioritization of Requirement")

# Load data if available
try:
    priority_data = pd.read_json(JSON_PRIO_DATA_PATH, orient='records')
except FileNotFoundError:
    priority_data = pd.DataFrame()

if not priority_data.empty:
    # Pre-populate inputs if data exists and session state is not already set
    if 'usecase' in priority_data.columns and 'usecase_select' not in st.session_state:
        st.session_state.usecase_select = priority_data['usecase'].iloc[0]
    if 'tool_integration' in priority_data.columns and 'tool_integration_input' not in st.session_state:
        st.session_state.tool_integration_input = priority_data['tool_integration'].iloc[0]
    if 'tool_usability' in priority_data.columns and 'tool_usability_input' not in st.session_state:
        st.session_state.tool_usability_input = priority_data['tool_usability'].iloc[0]
    if 'payment_method' in priority_data.columns and 'payment_method_select' not in st.session_state:
        st.session_state.payment_method_select = priority_data['payment_method'].iloc[0]
    if 'methodical_support' in priority_data.columns and 'methodical_support_input' not in st.session_state:
        st.session_state.methodical_support_input = priority_data['methodical_support'].iloc[0]
else:
    # Initialize session state with default values if no data is loaded.
    if 'usecase_select' not in st.session_state:
        st.session_state.usecase_select = None
    if 'payment_method_select' not in st.session_state:
        st.session_state.payment_method_select = []


col1, col2 = st.columns([1, 3])
col1.selectbox("Choose use case that you are in", UseCaseOptions, key="usecase_select")

# Add a number input that only allows values between 1 and 5
col1.number_input(
    "Tool-Integration",
    min_value=1,
    max_value=5,
    step=1,
    key="tool_integration_input",
)

col1.number_input(
    "Tool-Usability",
    min_value=1,
    max_value=10,
    step=1,
    key="tool_usability_input",
)

col1.multiselect(
  "Payment Method",
  PaymentMethodOptions,
  key="payment_method_select"
)

col1.number_input(
  "Methodical Support",
  min_value=1,
  max_value=10,
  step=1,
  key="methodical_support_input"
)

if st.button("💾 Save Prioritization"):
    data = {
        'usecase': st.session_state.usecase_select,
        'tool_integration': st.session_state.tool_integration_input,
        'tool_usability': st.session_state.tool_usability_input,
        'payment_method': st.session_state.payment_method_select,
        'methodical_support': st.session_state.methodical_support_input
    }
    export_data_to_json(pd.DataFrame([data]), JSON_PRIO_DATA_PATH)
    st.toast("Prioritization data saved successfully!", icon="💾")