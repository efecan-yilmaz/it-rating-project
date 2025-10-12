from utils.process_locator import determine_page, save_current_page, Page, run_redirect, clean_for_previous_direction
import streamlit as st
from utils.utils import JSON_DEFAULT_USE_CASES_PATH, load_from_json, JSON_SELECTED_USE_CASE_PATH
import pandas as pd

run_redirect(Page.READY_USE_CASE.value)

loaded_selected_use_case = load_from_json(JSON_SELECTED_USE_CASE_PATH)
selected_use_case = loaded_selected_use_case.get('selected_use_case', 'N/A');
st.header(f"Recommendations for Your Use Case: {selected_use_case}")

default_use_cases = load_from_json(JSON_DEFAULT_USE_CASES_PATH)

# Find the matching use case
matching = next((uc for uc in default_use_cases if uc["use_case"] == selected_use_case), None)

if matching:
  stack1 = matching.get("stack_1", [])
  stack2 = matching.get("stack_2", [])
  stack3 = matching.get("stack_3", [])

  def render_stack(stack, title):
    tools = stack.get("tools", [])
    justification = stack.get("justification", "")
    st.subheader(title)
    st.write(f"**Justification:** {justification}")
    for tool in tools:
      st.write(f"- {tool}")

  render_stack(stack1, "Recommended Tool Stack 1")
  st.write("---")
  render_stack(stack2, "Recommended Tool Stack 2")
  st.write("---")
  render_stack(stack3, "Recommended Tool Stack 3")

col_prev_next = st.columns([0.5, 0.5])
with col_prev_next[0]:
    if st.button("⬅️ Return to Welcome Page"):
        save_current_page(Page.WELCOME)
        clean_for_previous_direction(Page.READY_USE_CASE)
        st.switch_page(Page.WELCOME.value)


