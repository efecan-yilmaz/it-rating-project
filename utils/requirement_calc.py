import streamlit as st

def get_nfc_score(nfc):
  if nfc == "Nice to change":
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