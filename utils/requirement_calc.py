import streamlit as st

def get_nfc_score(nfc):
  if nfc == "No need to change":
    return 0
  elif nfc == "Nice to change":
    return 1
  elif nfc == "Must change":
    return 2
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
    return 0
  elif level == "Descriptive":
    return 1
  elif level == "Diagnostic":
    return 2
  elif level == "Predictive":
    return 3
  elif level == "Prescriptive":
    return 4
  else:
    return 0

def get_automation_score(option):
  if option == "Automated":
    return 0
  elif option == "AI-Asisted":
    return 1
  elif option == "AI-Driven Automation":
    return 2
  else:
    return 0

def get_sync_score(option):
  if option == "Ad-Hoc File Sharing":
    return 0
  elif option == "Planned Batch Exchange":
    return 1
  elif option == "Standardized Data Interfaces":
    return 2
  elif option == "Real-Time Ecosystem Integration":
    return 3
  else:
    return 0

def calculate_digitalization_score(tools_dict, def_tool_info):
  def_automation = def_tool_info.get("automation", 0)
  def_ai_level = def_tool_info.get("ai_level", 0)
  def_syncronization = def_tool_info.get("syncronization", 0)
  for tool_id, tool_info in tools_dict.items():
    digitalization_score = 0
    activities = tool_info["activities"]
    total_nfc = 0
    for activity in activities:
      automation_score = get_automation_score(activity.get("digitalization", "Automated"))
      ai_level_score = get_ai_score(activity.get("aiLevel", "No"))
      sync_score = get_sync_score(activity.get("synchronization", "Ad-Hoc File Sharing"))
      nfc_score = activity.get("nfc_score", 0)

      act_digi_score = 0
      if def_automation >= automation_score:
        act_digi_score += 1
      if def_ai_level >= ai_level_score:
        act_digi_score += 1
      if def_syncronization >= sync_score:
        act_digi_score += 1

      digitalization_score += nfc_score * (act_digi_score / 3)  # Normalize to [0, 1]
      total_nfc += nfc_score

    if "digitalization_score" not in def_tool_info:
      def_tool_info["digitalization_score"] = []
    if total_nfc == 0:
      score = 0
    else:
      score = digitalization_score / total_nfc if len(activities) > 0 else 0
    def_tool_info["digitalization_score"].append({"tool_id": tool_id, "score": score})
