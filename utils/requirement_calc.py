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
  
  return activity_calc / activity_count if activity_count > 0 else 0

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
    def_tool_info["preference_score"] = 0
    return
  # Assuming only one relevant row for the current usecase
  row = priority_data.iloc[0]
  user_usability = row.get("tool_usability", 0)
  user_support = row.get("methodical_support", 0)
  user_integration = row.get("tool_integration", 0)
  user_cost = row.get("cost", 0)
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
  st.write(f"User Weights - Usability: {user_usability}, Support: {user_support}, Integration: {user_integration}, Cost: {user_cost}")
  # calculate tool preference score
  def_tool_info["preference_score"] = calculate_tool_preference_score(def_tool_info, user_usability, user_support, user_integration, user_cost)

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

    def_tool_info["digitalization_score"].append({"tool_id": tool_id, "score": total_digi_score})
    def_tool_info["capability_score"].append({"tool_id": tool_id, "score": total_cap_score})

    # st.write(f"  Tool ID: {tool_id} - Digitalization Score: {score:.2f}")
