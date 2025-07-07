import streamlit as st

st.title("Measurement")
st.write("Enter the measurement data for the defined KPIs.")

col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
col1.selectbox(
  "Select KPI",
  ["KPI 1", "KPI 2", "KPI 3"],  # Replace with actual KPI options
  key="kpi_select"
)

col2.text_input("Related Activity Name", value="KPI 1", disabled=True, key="related_activity_input")

col3.text_input("Next Measurement Time (in months)", value="3", disabled=True, key="next_measurement_time_input")

cola, colb, colc = st.columns([1, 1, 3])
cola.text_input("X-Axis", disabled=True, value="X-Axis Name", key="x_axis_input")
colb.text_input(
  "X-Axis Value",
  key="x_axis_value_input"
)

cola.text_input("Y-Axis", disabled=True, value="Y-Axis Name")
colb.text_input(
  "Y-Axis Value",
  key="y_axis_value_input"
)

cola.text_input("Z-Axis", disabled=True, value="Z-Axis Name")
colb.text_input(
  "Z-Axis Value",
  key="z_axis_value_input"
)

if st.button("💾 Save Measurement"):
  st.toast("Measurement data saved successfully!", icon="💾")