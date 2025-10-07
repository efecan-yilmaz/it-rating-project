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

def calculate_def_tools_preference_scores(def_tool_info):
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

def calculate_digitalization_capability_scores(flat_activities, def_activities, def_automation, def_ai_level, def_syncronization):
  # digitalization score calculation
  digitalization_score = 0
  capability_score = 0
  total_nfc = 0
  for activity in flat_activities:
    automation_score = activity.get("digitalization", 0)
    ai_level_score = activity.get("aiLevel", 0)
    sync_score = activity.get("synchronization", 0)
    nfc_score = activity.get("nfc_score", 0)
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
    activity_name = activity.get("activity_name", "").strip().lower()
    matching_def_activity = next((def_act for def_act in def_activities if def_act.get("activity", "").strip().lower() == activity_name), None)
    if matching_def_activity:
      capability_score += nfc_score

    if total_nfc == 0:
      total_digi_score = 0
    else:
      total_digi_score = digitalization_score / total_nfc if total_nfc > 0 else 0

    if total_nfc == 0 or capability_score == 0:
      total_cap_score = 0
    else:
      total_cap_score = capability_score / total_nfc if total_nfc > 0 else 0
    
  return total_digi_score, total_cap_score


def find_highest_scorer(def_tools_data, flat_activities, force_all_activities=False):
  highest_scorer = None
  highest_score = -1
  flat_activity_names = {a.get("activity_name", "").strip().lower() for a in flat_activities}
  for def_tool_name, def_tool_info in def_tools_data.items():
    def_automation = def_tool_info.get("automation", -1)
    def_ai_level = def_tool_info.get("ai_level", -1)
    def_syncronization = def_tool_info.get("syncronization", -1)
    def_activities = def_tool_info.get("activities", [])
    def_activity_names = {a.get("activity", "").strip().lower() for a in def_activities}
    if force_all_activities and not flat_activity_names.issubset(def_activity_names):
      continue
    digi_score, cap_score = calculate_digitalization_capability_scores(
      flat_activities, def_activities, def_automation, def_ai_level, def_syncronization
    )
    total_score = float(digi_score * cap_score * def_tool_info.get("preference_score", 0.0))
    if total_score > highest_score:
      highest_score = total_score
      highest_scorer = {
        "tool_name": def_tool_name,
        "total_score": total_score,
        "digi_score": digi_score,
        "cap_score": cap_score,
        "preference_score": def_tool_info.get("preference_score", 0.0)
      }
  return highest_scorer

def run_forced_exchange_approach(tools_dict, def_tools_data):
  # st.write("### Forced Exchange Approach Results:")
  if not tools_dict:
    return []

  copy_tools_dict = tools_dict.copy()
  surpluss_activities = flatten_activities(copy_tools_dict, only_manual=True)

  ordered_tools = sorted(
    copy_tools_dict.items(),
    key=lambda item: item[1].get("prio_score", 0),
    reverse=True
  )
  def_tools_data_copy = def_tools_data.copy()
  results = []

  for tool_id, info in ordered_tools:
    flatten_tool_activities = flatten_activities({tool_id: info})
    highest = find_highest_scorer(def_tools_data_copy, flatten_tool_activities, True)
    # st.write(f"Forced Exchange - Highest for Tool ID {tool_id}")
    # st.write(highest)
    surpluss_activities.extend(flatten_tool_activities)
    if highest:
      cover_calcs(highest, surpluss_activities, def_tools_data_copy, results)
  
  # After looping through ordered_tools, cover any remaining surpluss_activities
  while surpluss_activities and def_tools_data_copy:
    highest = find_highest_scorer(def_tools_data_copy, surpluss_activities)
    if not highest:
      break
    cover_calcs(highest, surpluss_activities, def_tools_data_copy, results)

  # st.write(results)
  return results

def run_one_by_one_exchange_approach(tools_dict, def_tools_data):
  if not tools_dict:
    return []
  
  copy_tools_dict = tools_dict.copy()
  surpluss_activities = flatten_activities(copy_tools_dict, only_manual=True)
  # st.write(f"Surpluss Activities (Manual):")
  # st.write(surpluss_activities)
  
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
      digitalization_score = get_automation_score(activity.get("digitalization", "Automated"))
      ai_level_score = get_ai_score(activity.get("aiLevel", "No"))
      sync_score = get_sync_score(activity.get("synchronization", "Ad-Hoc File Sharing"))
      nfc_score = activity.get("nfc_score", 0)

      # Check if activity already exists in surpluss_activities
      existing = next((act for act in surpluss_activities if act["activity_name"] == activity_name), None)
      if existing:
        # Update scores if new ones are higher
        existing["digitalization"] = max(existing["digitalization"], digitalization_score)
        existing["aiLevel"] = max(existing["aiLevel"], ai_level_score)
        existing["synchronization"] = max(existing["synchronization"], sync_score)
        existing["nfc_score"] = max(existing["nfc_score"], nfc_score)
      else:
        surpluss_activities.append({
          "activity_name": activity_name,
          "digitalization": digitalization_score,
          "aiLevel": ai_level_score,
          "synchronization": sync_score,
          "nfc_score": nfc_score
        })
      
    highest = find_highest_scorer(def_tools_data_copy, surpluss_activities)
    cover_calcs(highest, surpluss_activities, def_tools_data_copy, results)

  # After looping through ordered_tools, cover any remaining surpluss_activities
  while surpluss_activities and def_tools_data_copy:
    highest = find_highest_scorer(def_tools_data_copy, surpluss_activities)
    if not highest:
      break
    cover_calcs(highest, surpluss_activities, def_tools_data_copy, results)

  # st.write("### One-by-One Exchange Approach Results:")
  # st.write(results)
  return results

def flatten_activities(tools_dict, only_manual=False):
  flat_activities = []
  activity_map = {}
  tools_to_remove = set()

  for tool_id, info in tools_dict.items():
    activities = info.get("activities", []) or []
    for activity in activities:
      if not isinstance(activity, dict):
        continue
      if only_manual and not activity.get("isManual", False):
        continue
      activity_name = activity.get("category", "N/A").strip().lower()
      digitalization_score = get_automation_score(activity.get("digitalization", "Automated"))
      ai_level_score = get_ai_score(activity.get("aiLevel", "No"))
      sync_score = get_sync_score(activity.get("synchronization", "Ad-Hoc File Sharing"))
      nfc_score = activity.get("nfc_score", 0)

      if activity_name in activity_map:
        prev = activity_map[activity_name]
        activity_map[activity_name] = {
          "activity_name": activity_name,
          "digitalization": max(prev["digitalization"], digitalization_score),
          "aiLevel": max(prev["aiLevel"], ai_level_score),
          "synchronization": max(prev["synchronization"], sync_score),
          "nfc_score": max(prev["nfc_score"], nfc_score)
        }
      else:
        activity_map[activity_name] = {
          "activity_name": activity_name,
          "digitalization": digitalization_score,
          "aiLevel": ai_level_score,
          "synchronization": sync_score,
          "nfc_score": nfc_score
        }
        if only_manual:
          tools_to_remove.add(tool_id)

  flat_activities = list(activity_map.values())

  # Remove tools from tools_dict if only_manual is True and they contributed activities
  if only_manual:
    for tool_id in tools_to_remove:
      tools_dict.pop(tool_id, None)

  return flat_activities

def run_total_score_prioritization(tools_dict, def_tools_data):
  if not tools_dict:
    return []
  
  flat_activities = flatten_activities(tools_dict)
  # st.write(f"Flat Activities: {flat_activities}")
  def_tools_data_copy = def_tools_data.copy()
  results = []

  while flat_activities and def_tools_data_copy:
    highest = find_highest_scorer(def_tools_data_copy, flat_activities)
    if not highest:
      break
    cover_calcs(highest, flat_activities, def_tools_data_copy, results)

  # st.write("### Total Score Prioritization Results:")
  # st.write(results)
  return results

def cover_calcs(highest, flat_activities, def_tools_data_copy, results):
  tool_name = highest["tool_name"]
  score = highest["total_score"]
  tool_info = def_tools_data_copy.get(tool_name, {})
  activities = tool_info.get("activities", [])
  # Find which activities this tool covers
  covered = []
  for activity in activities:
    activity_name = activity.get("activity", "N/A").strip().lower()
    for flat_act in flat_activities:
      if flat_act.get("activity_name", "").strip().lower() == activity_name:
        covered.append(activity_name)
        break
  if covered:
    results.append({"tool_name": tool_name, "score": score, "activities": covered})
    # Remove covered activities from flat_activities
    flat_activities[:] = [fa for fa in flat_activities if fa.get("activity_name", "").strip().lower() not in covered]
  # Remove this tool from further consideration
  def_tools_data_copy.pop(tool_name, None)