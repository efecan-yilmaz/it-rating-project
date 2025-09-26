import streamlit as st

from utils.utils import (
    JSON_RE_DETAILS_DATA_PATH,
    load_details_data_from_json,
    load_def_tools_data_from_xlsx
)

from utils.process_locator import determine_page, save_current_page, Page, run_redirect, clean_for_previous_direction

from utils.requirement_calc import tool_priorizitation, calculate_def_tools_preference_scores, run_total_score_prioritization, run_one_by_one_exchange_approach, run_forced_exchange_approach

st.title("Desigin Recommendation")

# Load data
details_df = load_details_data_from_json(JSON_RE_DETAILS_DATA_PATH)

# data structure:
# {tool_id: {"activities": [activity_dicts], "prio_score": float}}

# Find tools and related activities using base_tool_id
tools_list = details_df['base_tool_id'].dropna().unique().tolist()
tools_dict = {
  tool_id: {"activities": details_df[details_df['base_tool_id'] == tool_id].to_dict(orient='records'), "tool_name": details_df[details_df['base_tool_id'] == tool_id]['tool'].iloc[0]}
  for tool_id in tools_list
}

for tool_id, tool_info in tools_dict.items():
  activities = tool_info["activities"]
  tool_name = tool_info["tool_name"]
  prio_score = tool_priorizitation(activities)  # Pass activities list
  tools_dict[tool_id]['prio_score'] = prio_score  # Add prio_score to tools_dict
  st.header(f"Tool Name: {tool_name} - Tool ID: {tool_id} - Prioritization Score: {prio_score:.2f}")
  for activity in activities:
    #st.write(f"  Activity ID: {activity.get('id', 'N/A')} - Activity Name: {activity.get('tool', 'N/A')} - Need For Change: {activity.get('needForChange', 'N/A')} - NFC Score: {activity.get('nfc_score', 0)}")
    st.write(activity)

# load def_tool_data
def_tools_data = load_def_tools_data_from_xlsx()

for tool_name, def_tool_info in def_tools_data.items():
  activities = def_tool_info.get("activities", [])
  calculate_def_tools_preference_scores(def_tool_info)

run_total_score_prioritization(tools_dict, def_tools_data)
run_one_by_one_exchange_approach(tools_dict, def_tools_data)
run_forced_exchange_approach(tools_dict, def_tools_data)


  # calculate_def_tool_scores(tools_dict, def_tool_info)
  # st.write(f"Activities: {activities}")
  # st.write(f"Automation: {def_tool_info.get('automation', 'N/A')}")
  # st.write(f"AI Level: {def_tool_info.get('ai_level', 'N/A')}")
  # st.write(f"Syncronization: {def_tool_info.get('syncronization', 'N/A')}")
  # st.write(f"Integration: {def_tool_info.get('integration', 'N/A')}")
  # st.write(f"Usability: {def_tool_info.get('usability', 'N/A')}")
  # st.write(f"Cost: {def_tool_info.get('cost', 'N/A')}")
  # st.write(f"Support: {def_tool_info.get('support', 'N/A')}")
  # st.write(f"Functionality: {def_tool_info.get('functionality', 'N/A')}")
  # st.write(f"Digitalization Score: {def_tool_info.get('digitalization_score', 'N/A')}")
  # st.write(f"Preference Score: {def_tool_info.get('preference_score', 'N/A')}")
  # st.write(f"Capability Score: {def_tool_info.get('capability_score', 'N/A')}")
  # st.write(f"Total Score: {def_tool_info.get('total_score', 'N/A')}")

# total_score_prio_result = calc_total_score_prioritization(tools_dict, def_tools_data)
# total_score_one_by_one_result = calc_one_by_one_exchange_approach(tools_dict, def_tools_data)

# st.header("### Final Recommendation Scores")
# st.write("The total score prio results:")
# st.write(total_score_prio_result)

# st.write("The one-by-one exchange approach results:")
# st.write(total_score_one_by_one_result)

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