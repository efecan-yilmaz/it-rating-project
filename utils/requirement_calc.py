import streamlit as st
import pandas as pd

from utils.utils import (
    JSON_PRIO_DATA_PATH,
)

def get_nfc_score(nfc):
  if nfc == "No need to change":
    return 1
  elif nfc == "Nice to change":
    return 2
  elif nfc == "Must change":
    return 3
  else:
    return 0

def tool_priorizitation(activities):
  activity_count = len(activities)
  activity_calc = 0
  for activity in activities:
    nfc = activity.get("needForChange", "No need to change")
    nfc_score = get_nfc_score(nfc)
    activity["nfc_score"] = nfc_score  # Store the score back in the activity
    activity_calc += nfc_score
  
  return float(activity_calc / activity_count) if activity_count > 0 else 0

def get_ai_score(level):
  if level == "No":
    return 1
  elif level == "Descriptive":
    return 2
  elif level == "Diagnostic":
    return 3
  elif level == "Predictive":
    return 4
  elif level == "Prescriptive":
    return 5
  else:
    return 0

def get_automation_score(option):
  if option == "Automated":
    return 1
  elif option == "AI-Asisted":
    return 2
  elif option == "AI-Driven Automation":
    return 3
  else:
    return 0

def get_sync_score(option):
  if option == "Ad-Hoc File Sharing":
    return 1
  elif option == "Planned Batch Exchange":
    return 2
  elif option == "Standardized Data Interfaces":
    return 3
  elif option == "Real-Time Ecosystem Integration":
    return 4
  else:
    return 0
  
def read_user_preference_scores(def_tool_info):
  try:
    priority_data = pd.read_json(JSON_PRIO_DATA_PATH, orient='records')
  except FileNotFoundError:
    priority_data = pd.DataFrame()
  if priority_data.empty:
    def_tool_info["preference_score"] = 0.0
    return
  # Assuming only one relevant row for the current usecase
  row = priority_data.iloc[0]
  user_usability = float(row.get("tool_usability", 0) or 0)
  user_support = float(row.get("methodical_support", 0) or 0)
  user_integration = float(row.get("tool_integration", 0) or 0)
  user_cost = float(row.get("cost", 0) or 0)
  return user_usability, user_support, user_integration, user_cost

def calculate_tool_preference_score(def_tool_info, user_usability, user_support, user_integration, user_cost):
  def_tool_integration = def_tool_info.get("integration", 0)
  def_tool_usability = def_tool_info.get("usability", 0)
  def_tool_cost = def_tool_info.get("cost", 0)
  def_tool_support = def_tool_info.get("support", 0)
  def_tool_functionality = def_tool_info.get("functionality", 0)

  return ((def_tool_usability * user_usability) +
          (def_tool_support * user_support) +
          (def_tool_integration * user_integration) +
          (def_tool_cost * user_cost) +
          (def_tool_functionality) * 5) / (25 * (user_usability + user_support + user_integration + user_cost + 5))



def calculate_def_tool_scores(tools_dict, def_tool_info):
  # Read user preference scores
  user_scores = read_user_preference_scores(def_tool_info)
  if user_scores:
    user_usability, user_support, user_integration, user_cost = user_scores
  else:
    user_usability = user_support = user_integration = user_cost = 0
  # st.write(f"User Weights - Usability: {user_usability}, Support: {user_support}, Integration: {user_integration}, Cost: {user_cost}")
  # calculate tool preference score
  def_tool_info["preference_score"] = float(
    calculate_tool_preference_score(def_tool_info, user_usability, user_support, user_integration, user_cost)
  )

  def_automation = def_tool_info.get("automation", -1)
  def_ai_level = def_tool_info.get("ai_level", -1)
  def_syncronization = def_tool_info.get("syncronization", -1)
  # st.subheader(f"Calculating Digitalization Scores for Def Tool: {def_tool_info}")
  for tool_id, tool_info in tools_dict.items():
    digitalization_score = 0
    capability_score = 0
    activities = tool_info["activities"]
    total_nfc = 0
    for activity in activities:
      # digitalization score calculation
      # st.subheader(f"  Evaluating Activity: {activity}")
      # st.write(f"    Def Tool Automation: {def_automation}, AI Level: {def_ai_level}, Syncronization: {def_syncronization}")
      automation_score = get_automation_score(activity.get("digitalization", "Automated"))
      ai_level_score = get_ai_score(activity.get("aiLevel", "No"))
      sync_score = get_sync_score(activity.get("synchronization", "Ad-Hoc File Sharing"))
      nfc_score = activity.get("nfc_score", 0)
      # st.write(f"    Activity Automation Score: {automation_score}, AI Level Score: {ai_level_score}, Sync Score: {sync_score}, NFC Score: {nfc_score}")

      act_digi_score = 0
      if def_automation >= automation_score and def_automation > -1:
        act_digi_score += 1
      if def_ai_level >= ai_level_score and def_ai_level > -1:
        act_digi_score += 1
      if def_syncronization >= sync_score and def_syncronization > -1:
        act_digi_score += 1

      digitalization_score += nfc_score * (act_digi_score / 3)  # Normalize to [0, 1]
      total_nfc += nfc_score

      # capability score calculation
      # find the matching def tool activity
      def_activities = def_tool_info.get("activities", [])
      activity_name = activity.get("category", "").strip().lower()
      matching_def_activity = next((def_act for def_act in def_activities if def_act.get("activity", "").strip().lower() == activity_name), None)
      if matching_def_activity:
        capability_score += nfc_score

    if "digitalization_score" not in def_tool_info:
      def_tool_info["digitalization_score"] = []
    if total_nfc == 0:
      total_digi_score = 0
    else:
      total_digi_score = digitalization_score / total_nfc if len(activities) > 0 else 0

    if "capability_score" not in def_tool_info:
      def_tool_info["capability_score"] = []
    if total_nfc == 0 or capability_score == 0:
      total_cap_score = 0
    else:
      total_cap_score = capability_score / total_nfc if len(activities) > 0 else 0

    # Ensure total_score list exists before appending to it
    if "total_score" not in def_tool_info:
      def_tool_info["total_score"] = []

    def_tool_info["digitalization_score"].append({"tool_id": tool_id, "score": total_digi_score})
    def_tool_info["capability_score"].append({"tool_id": tool_id, "score": total_cap_score})
    def_tool_info["total_score"].append({
      "tool_id": tool_id,
      "score": float(total_digi_score * total_cap_score + def_tool_info.get("preference_score", 0.0))
    })

    # st.write(f"  Tool ID: {tool_id} - Digitalization Score: {score:.2f}")

def find_highest_scorer(def_tools_data):
  highest_scorer = None
  highest_score = -1
  for tool_name, def_tool_info in def_tools_data.items():
    total_scores = def_tool_info.get("total_score", [])
    for score_entry in total_scores:
      score = score_entry.get("score", 0)
      if score > highest_score:
        highest_score = score
        highest_scorer = (tool_name, score)
  return highest_scorer

def calc_total_score_prioritization(tools_dict, def_tools_data):
  if not tools_dict:
    return []

  flat_activities = []
  for tool_id, info in tools_dict.items():
    activities = info.get("activities", []) or []
    for activity in activities:
      if not isinstance(activity, dict):
        continue
      activity_name = activity.get("category", "N/A").strip().lower()
      if activity_name not in flat_activities:
        flat_activities.append(activity_name.strip().lower())

  def_tools_data_copy = def_tools_data.copy()
  results = []

  while flat_activities and def_tools_data_copy:
    highest = find_highest_scorer(def_tools_data_copy)
    if not highest:
      break
    cover_calcs(highest, flat_activities, def_tools_data_copy, results)

  return results

def cover_calcs(highest, flat_activities, def_tools_data_copy, results):
  tool_name, score = highest
  tool_info = def_tools_data_copy.get(tool_name, {})
  activities = tool_info.get("activities", [])
  # Find which activities this tool covers
  covered = []
  for activity in activities:
    activity_name = activity.get("activity", "N/A").strip().lower()
    if activity_name in flat_activities:
      covered.append(activity_name)
  if covered:
    results.append({"tool_name": tool_name, "score": score, "activities": covered})
    for act in covered:
      if act in flat_activities:
        flat_activities.remove(act)
  # Remove this tool from further consideration
  def_tools_data_copy.pop(tool_name)
  # If no activities matched, just continue

def calc_one_by_one_exchange_approach(tools_dict, def_tools_data):
  if not tools_dict:
    return []
  copy_tools_dict = tools_dict.copy()
  surpluss_activities = []
  for tool_id, info in list(copy_tools_dict.items()):
    activities = info.get("activities", []) or []
    for activity in activities:
      if activity.get("isManual") == True:
        activity_name = activity.get("category", "N/A").strip().lower()
        if activity_name not in surpluss_activities:
          surpluss_activities.append(activity_name)
        del copy_tools_dict[tool_id]
        break
  
  ordered_tools = sorted(
    copy_tools_dict.items(),
    key=lambda item: item[1].get("prio_score", 0),
    reverse=True
  )
  def_tools_data_copy = def_tools_data.copy()
  results = []

  for tool_id, info in ordered_tools:
    activities = info.get("activities", []) or []
    for activity in activities:
      activity_name = activity.get("category", "N/A").strip().lower()
      if activity_name not in surpluss_activities:
        surpluss_activities.append(activity_name)
      
    highest = find_highest_scorer(def_tools_data_copy)
    cover_calcs(highest, surpluss_activities, def_tools_data_copy, results)

  # After looping through ordered_tools, cover any remaining surpluss_activities
  while surpluss_activities and def_tools_data_copy:
    highest = find_highest_scorer(def_tools_data_copy)
    if not highest:
      break
    cover_calcs(highest, surpluss_activities, def_tools_data_copy, results)

  return results




