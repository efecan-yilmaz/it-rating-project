from unittest import result
import streamlit as st

from utils.utils import (
    JSON_RE_DETAILS_DATA_PATH,
    load_details_data_from_json,
    load_def_tools_data_from_xlsx
)

from utils.process_locator import determine_page, save_current_page, Page, run_redirect, clean_for_previous_direction

from utils.requirement_calc import read_user_preference_scores, tool_priorizitation, calculate_def_tools_preference_scores, run_total_score_prioritization, run_one_by_one_exchange_approach, run_forced_exchange_approach
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

run_redirect(Page.REQUIREMENT.value)

st.title("Desigin Recommendation")


# Load data
details_df = load_details_data_from_json(JSON_RE_DETAILS_DATA_PATH)

# data structure:
# {tool_id: {"activities": [activity_dicts]}

# Find tools and related activities using base_tool_id
tools_list = details_df['base_tool_id'].dropna().unique().tolist()
tools_dict = {
  tool_id: {"activities": details_df[details_df['base_tool_id'] == tool_id].to_dict(orient='records'), "tool_name": details_df[details_df['base_tool_id'] == tool_id]['tool'].iloc[0]}
  for tool_id in tools_list
}

# Define color mapping for Need for Change
color_map = {
  "No need to change": "background-color: #e0e0e0;",   # gray
  "Nice to change": "background-color: #ffa500;",      # orange
  "Must change": "background-color: #ff4c4c;"          # red
}

col_main = st.columns([0.5, 0.5])
with col_main[0]:
  st.header("Current Tool Stack")
  st.write("---")
  st.header("Tools and Their Activities")
  for tool_id, tool_info in tools_dict.items():
    activities = tool_info["activities"]
    tool_name = tool_info["tool_name"]
    # Check for single manual activity
    if len(activities) == 1 and activities[0].get('isManual', False):
      st.subheader("Activities for Tool: Manual Task")
    else:
      st.subheader(f"Activities for Tool: {tool_name}")
    if activities:
      activity_df = pd.DataFrame(activities)
      # Rename columns as requested
      rename_map = {
        'needForChange': 'Need for Change',
        'voe': 'VoE',
        'digitalization': 'Digitalization',
        'aiLevel': 'AI Level',
        'synchronization': 'Synchronization'
      }
      activity_df = activity_df.rename(columns=rename_map)
      # Hide 'id', 'isManual', 'base_tool_id', and 'tool' columns in the displayed table
      cols_to_hide = ['id', 'isManual', 'base_tool_id', 'tool', 'colloborative', 'paymentMethod']
      visible_cols = [col for col in activity_df.columns if col not in cols_to_hide]
      if 'category' in visible_cols:
        visible_cols.remove('category')
        visible_cols = ['category'] + visible_cols
        activity_df = activity_df.rename(columns={'category': 'Activity'})
        visible_cols[0] = 'Activity'

      def highlight_row(row):
        nfc = row.get('Need for Change', '')
        return [color_map.get(nfc, "") for _ in row]

      styled_df = activity_df[visible_cols].style.apply(highlight_row, axis=1)
      st.write(styled_df)
    else:
      st.write("No activities found for this tool.")

for tool_id, tool_info in tools_dict.items():
  activities = tool_info["activities"]
  tool_name = tool_info["tool_name"]
  prio_score = tool_priorizitation(activities)  # Pass activities list
  tools_dict[tool_id]['prio_score'] = prio_score  # Add prio_score to tools_dict
  # st.header(f"Tool Name: {tool_name} - Tool ID: {tool_id} - Prioritization Score: {prio_score:.2f}")
  # for activity in activities:
  #   #st.write(f"  Activity ID: {activity.get('id', 'N/A')} - Activity Name: {activity.get('tool', 'N/A')} - Need For Change: {activity.get('needForChange', 'N/A')} - NFC Score: {activity.get('nfc_score', 0)}")
  #   st.write(activity)

# load def_tool_data
def_tools_data = load_def_tools_data_from_xlsx()
user_scores = read_user_preference_scores()
if user_scores:
  user_usability, user_support, user_integration, user_cost, user_payment = user_scores
else:
  user_usability = user_support = user_integration = user_cost = 0
  user_payment = [1]


for tool_name, def_tool_info in def_tools_data.items():
  activities = def_tool_info.get("activities", [])
  calculate_def_tools_preference_scores(def_tool_info, user_usability, user_support, user_integration, user_cost)

with col_main[1]:
  st.header("Recommendation Results")

  # add PDF generator helper
  def generate_recommendation_pdf(tools_dict, approaches):
    """
    approaches: list of tuples (title, score, result_list)
      where result_list is the list produced by each approach (tool result dicts).
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
    styles = getSampleStyleSheet()
    flow = []
    flow.append(Paragraph("Recommendation Report", styles['Title']))
    flow.append(Spacer(1, 12))

    def get_max_nfc_for_activity(activity_name):
      order = {"Must change": 3, "Nice to change": 2, "No need to change": 1}
      max_nfc = None
      for tool in tools_dict.values():
        for act in tool["activities"]:
          cat = (act.get("category") or "").strip().lower()
          if cat and cat == (activity_name or "").strip().lower():
            nfc = act.get("needForChange", "")
            if max_nfc is None or order.get(nfc, 0) > order.get(max_nfc, 0):
              max_nfc = nfc
      return max_nfc or ""

    for title, score, results in approaches:
      flow.append(Paragraph(f"{title} - Recommendation Score: {score * 100:.2f}%" if results else f"{title} - Recommendation Score: N/A", styles['Heading2']))
      flow.append(Spacer(1, 6))
      if not results:
        flow.append(Paragraph("No recommendation returned for this approach.", styles['Normal']))
        flow.append(Spacer(1, 8))
        continue

      # build a simple table: Tool | Activities (with Need For Change)
      table_data = [["Tool", "Activities (Need For Change)"]]
      for tr in results:
        tname = tr.get("tool_name", "Unknown")
        acts = tr.get("activities", [])
        # activities may be list of strings or dicts with 'category'
        display_acts = []
        for a in acts:
          if isinstance(a, dict):
            act_name = a.get("category", "")
          else:
            act_name = a
          nfc = get_max_nfc_for_activity(act_name)
          if act_name:
            display_acts.append(f"{act_name.capitalize()} ({nfc})")
        table_data.append([tname, "\n".join(display_acts)])
      t = Table(table_data, colWidths=[160, 360])
      t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#f0f0f0")),
        ('GRID',(0,0),(-1,-1),0.5,colors.grey),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
      ]))
      flow.append(t)
      flow.append(Spacer(1, 12))

    doc.build(flow)
    buf.seek(0)
    return buf.read()

  def display_recommendation_results(result_data, payment_flag=True):
    if not payment_flag:
      st.warning(f"Couldn't find a recommendation that fits your payment method preferences. Showing best possible match without considering payment method.")
    for tool_result in result_data:
      tool_name = tool_result.get("tool_name", "Unknown Tool")
      activities = tool_result.get("activities", [])
      st.subheader(f"{tool_name}")
      st.write(f"Automation: {tool_result.get('automation', 'N/A')}")
      st.write(f"AI Level: {tool_result.get('ai_level', 'N/A')}")
      st.write(f"Syncronization: {tool_result.get('synchronization', 'N/A')}")
      
      if activities:
        # Find matching activities from tools_dict by 'Activity' (category)
        activity_df = pd.DataFrame(activities, columns=["Activity"])
        if "Activity" in activity_df.columns:
          # Capitalize first letter of each activity
          activity_df["Activity"] = activity_df["Activity"].apply(lambda x: x.capitalize() if isinstance(x, str) else x)

          def get_max_need_for_change(activity_name):
            max_nfc = None
            for tool in tools_dict.values():
              for act in tool["activities"]:
                if act.get("category").strip().lower() == activity_name.lower():
                  nfc = act.get("needForChange", "")
                  # Order: Must change > Nice to change > No need to change
                  order = {"Must change": 3, "Nice to change": 2, "No need to change": 1}
                  if max_nfc is None or order.get(nfc, 0) > order.get(max_nfc, 0):
                    max_nfc = nfc
            return max_nfc

          # Add 'Need For Change' column
          activity_df["Need For Change"] = activity_df["Activity"].apply(
            lambda x: get_max_need_for_change(x)
          )

          def highlight_row(row):
            nfc = row.get("Need For Change", "")
            return [color_map.get(nfc, "") for _ in row]

          styled_df = activity_df.style.apply(highlight_row, axis=1)
          st.write(styled_df)
        else:
          st.table(activity_df)
      else:
        st.write("No activities found for this tool.")

  def check_if_all_activities_covered(tools_dict, result_data):
    all_activities = set()
    for tool in tools_dict.values():
      for activity in tool["activities"]:
        category = activity.get("category", "").strip().lower()
        if category:
          all_activities.add(category)

    covered_activities = set()
    for tool in result_data:
      for activity in tool.get("activities", []):
        if isinstance(activity, str):
          category = activity.strip().lower()
        elif isinstance(activity, dict):
          category = activity.get("category", "").strip().lower()
        else:
          continue
        if category:
          covered_activities.add(category)

    uncovered_activities = all_activities - covered_activities
    if not uncovered_activities:
      return True
    return False

  st.write("---")
  total_score_payment_flag = True
  [total_score_prio_result, total_score_prio_score] = run_total_score_prioritization(tools_dict, def_tools_data, user_payment)
  if not check_if_all_activities_covered(tools_dict, total_score_prio_result):
    [total_score_prio_result, total_score_prio_score] = run_total_score_prioritization(tools_dict, def_tools_data)
    total_score_payment_flag = False

  one_by_one_payment_flag = True
  [one_bye_one_exchange_result, one_by_one_score] = run_one_by_one_exchange_approach(tools_dict, def_tools_data, user_payment)
  if not check_if_all_activities_covered(tools_dict, one_bye_one_exchange_result):
    [one_bye_one_exchange_result, one_by_one_score] = run_one_by_one_exchange_approach(tools_dict, def_tools_data)
    one_by_one_payment_flag = False

  forced_exchange_payment_flag = True
  [forced_exchange_result, forced_exchange_score] = run_forced_exchange_approach(tools_dict, def_tools_data, user_payment)
  if not check_if_all_activities_covered(tools_dict, forced_exchange_result):
    [forced_exchange_result, forced_exchange_score] = run_forced_exchange_approach(tools_dict, def_tools_data)
    forced_exchange_payment_flag = False

  # Prepare approaches and generate PDF for download (download button placed at top)
  approaches = [
    ("Total Score Prioritization Approach", total_score_prio_score or 0.0, total_score_prio_result),
    ("One-by-One Exchange Approach", one_by_one_score or 0.0, one_bye_one_exchange_result),
    ("Forced Exchange Approach", forced_exchange_score or 0.0, forced_exchange_result),
  ]
  pdf_bytes = generate_recommendation_pdf(tools_dict, approaches)
  st.download_button(label="⬇️ Download Recommendation Report", data=pdf_bytes, file_name="recommendation_report.pdf", mime="application/pdf")

  st.header(f"Total Score Prioritization Approach - Recommendation Score: {total_score_prio_score * 100:.2f}%" if total_score_prio_result else "Total Score Prioritization Approach - Recommendation Score: N/A")
  display_recommendation_results(total_score_prio_result, total_score_payment_flag)
  st.write("---")

  st.header(f"One-by-One Exchange Approach - Recommendation Score: {one_by_one_score * 100:.2f}%" if one_bye_one_exchange_result else "One-by-One Exchange Approach - Recommendation Score: N/A")
  display_recommendation_results(one_bye_one_exchange_result, one_by_one_payment_flag)
  st.write("---")

  st.header(f"Forced Exchange Approach - Recommendation Score: {forced_exchange_score * 100:.2f}%" if forced_exchange_result else "Forced Exchange Approach - Recommendation Score: N/A")
  display_recommendation_results(forced_exchange_result, forced_exchange_payment_flag)


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
# with col_prev_next[1]:
#   if st.button("➡️ Next step"):
#     save_current_page(Page.REQUIREMENT)
#     st.switch_page(Page.REQUIREMENT.value)
