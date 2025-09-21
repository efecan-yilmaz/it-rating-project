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