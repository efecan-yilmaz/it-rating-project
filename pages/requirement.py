import streamlit as st

from utils.utils import (
    JSON_RE_DETAILS_DATA_PATH,
    load_details_data_from_json,
    load_def_tools_data_from_xlsx
)

from utils.process_locator import determine_page, save_current_page, Page, run_redirect, clean_for_previous_direction

from utils.requirement_calc import tool_priorizitation, calculate_digitalization_score

st.title("Desigin Recommendation")

# Load data
details_df = load_details_data_from_json(JSON_RE_DETAILS_DATA_PATH)

# data structure:
# {tool_id: {"activities": [activity_dicts], "prio_score": float}}

# Find tools and related activities using base_tool_id
tools_list = details_df['base_tool_id'].dropna().unique().tolist()
tools_dict = {
  tool_id: {"activities": details_df[details_df['base_tool_id'] == tool_id].to_dict(orient='records')}
  for tool_id in tools_list
}

for tool_id, tool_info in tools_dict.items():
  activities = tool_info["activities"]
  prio_score = tool_priorizitation(activities)  # Pass activities list
  tools_dict[tool_id]['prio_score'] = prio_score  # Add prio_score to tools_dict
  st.header(f"Tool ID: {tool_id} - Prioritization Score: {prio_score:.2f}")
  for activity in activities:
    #st.write(f"  Activity ID: {activity.get('id', 'N/A')} - Activity Name: {activity.get('tool', 'N/A')} - Need For Change: {activity.get('needForChange', 'N/A')} - NFC Score: {activity.get('nfc_score', 0)}")
    st.write(activity)

# load def_tool_data
def_tools_data = load_def_tools_data_from_xlsx()

for tool_name, def_tool_info in def_tools_data.items():
  st.header(f"Tool: {tool_name}")
  activities = def_tool_info.get("activities", [])
  calculate_digitalization_score(tools_dict, def_tool_info)
  st.write(f"Activities: {activities}")
  st.write(f"Automation: {def_tool_info.get('automation', 'N/A')}")
  st.write(f"AI Level: {def_tool_info.get('ai_level', 'N/A')}")
  st.write(f"Syncronization: {def_tool_info.get('syncronization', 'N/A')}")
  st.write(f"Digitalization Score: {def_tool_info.get('digitalization_score', 'N/A')}")



col_prev_next = st.columns([0.5, 0.5])
with col_prev_next[0]:
  if st.button("⬅️ Previous step"):
    save_current_page(Page.REQUIREMENT_ENGINEERING)
    clean_for_previous_direction(Page.REQUIREMENT)
    st.switch_page(Page.REQUIREMENT_ENGINEERING.value)
with col_prev_next[1]:
  if st.button("➡️ Next step"):
    save_current_page(Page.REQUIREMENT)
    st.switch_page(Page.REQUIREMENT.value)