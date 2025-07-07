import streamlit as st
from data.SelectValues import KPITypeOptions, VisualizationMethodOptions

st.title("Define KPI")
st.write("Define your Key Performance Indicators (KPIs) for selected tools and manual tasks.")

col1, col2, col3 = st.columns([1, 1, 1])

col1.selectbox(
  "Related Activity",
  ["Selected KPI1", "Selected KPI2", "Selected KPI3"],
  key="related_activity_select"
)

col2.text_input(
  "KPI Name",
  key="kpi_name_input"
)

col3.selectbox(
  "KPI Type",
  KPITypeOptions,
  key="kpi_type_select"
)

col1.selectbox(
  "Visualization Method",
  VisualizationMethodOptions,
  key="visualization_method_select"
)

col2.number_input(
  "Measurement Period (in months)",
  min_value=0,
  max_value=12,
  step=1,
  key="measurement_period_input"
)

col3.text_input(
  "Measurement Responsible",
  key="measurement_responsible_input"
)

cola, colb, colc = st.columns([1, 1, 3])

cola.text_input(
  "x",
  key="x_axis_input",
)

colb.selectbox(
  "Data Type",
  ["Numeric", "Text", "Date", "Boolean"],
  key="data_type_x_select"
)

cola.text_input(
  "y",
  key="y_axis_input",
)

colb.selectbox(
  "Data Type",
  ["Numeric", "Text", "Date", "Boolean"],
  key="data_type_y_select"
)

cola.text_input(
  "z",
  key="z_axis_input",
)

colb.selectbox(
  "Data Type",
  ["Numeric", "Text", "Date", "Boolean"],
  key="data_type_z_select"
)

if st.button("💾 Save KPI"):
  st.toast("KPI data saved successfully!", icon="💾")