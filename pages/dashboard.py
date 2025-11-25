import streamlit as st
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


st.title("Dashboard")
st.write("Welcome to the KPI Dashboard. Here you can get an overview of your defined KPIs and their measurements.")

# --- Data Loading ---
BASE_DIR = Path(__file__).resolve().parent.parent
KPI_DEFS_FILE = BASE_DIR / "data" / "kpi" / "kpi_defs.json"
MEASUREMENTS_DIR = BASE_DIR / "data" / "kpi" / "measurements"

def load_kpis():
    """Loads all KPI definitions."""
    if KPI_DEFS_FILE.exists():
        try:
            with KPI_DEFS_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def load_measurement_data(kpi_id):
    """Loads measurement data for a specific KPI ID."""
    measurement_file = MEASUREMENTS_DIR / f"{kpi_id}.json"
    if measurement_file.exists():
        try:
            with measurement_file.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

# --- Main Dashboard ---
kpis = load_kpis()

if not kpis:
    st.warning("No KPIs defined yet. Please go to the 'Define KPI' page to create a KPI first.")
    st.stop()

# Create columns for a 2-column layout
cols = st.columns(2)
col_idx = 0

for kpi in kpis:
    kpi_id = kpi["id"]
    kpi_name = kpi["name"]
    viz_type = kpi["visualization"]
    mappings = kpi.get("mappings", {})
    
    measurements = load_measurement_data(kpi_id)
    
    # Use the current column
    current_col = cols[col_idx % 2]

    with current_col:
        st.subheader(kpi_name)

        if not measurements:
            st.info("No measurement data available for this KPI.")
            col_idx += 1
            continue

        df = pd.DataFrame(measurements)
        fig = None

        try:
            if viz_type == "Line Chart":
                x_label = mappings.get("x", {}).get("label")
                y_label = mappings.get("y", {}).get("label")
                if x_label and y_label and x_label in df.columns and y_label in df.columns:
                    if mappings.get("x", {}).get("type") == "Date":
                        df[x_label] = pd.to_datetime(df[x_label])
                    fig = px.line(df, x=x_label, y=y_label, title=kpi_name)

            elif viz_type == "Multi-Line Chart":
                x_label = mappings.get("x", {}).get("label")
                if x_label and x_label in df.columns:
                    if mappings.get("x", {}).get("type") == "Date":
                        df[x_label] = pd.to_datetime(df[x_label])
                    
                    y_series_labels = [info['label'] for key, info in mappings.items() if key.startswith('y_series_') and 'label' in info]
                    valid_y_series = [label for label in y_series_labels if label in df.columns]
                    
                    if valid_y_series:
                        df_long = df.melt(id_vars=[x_label], value_vars=valid_y_series, var_name='Series', value_name='Value')
                        fig = px.line(df_long, x=x_label, y='Value', color='Series', title=kpi_name)

            elif viz_type == "Bar Chart":
                x_label = mappings.get("x", {}).get("label")
                y_label = mappings.get("y", {}).get("label")
                
                if kpi.get("bar_grouped"):
                    y_series_labels = [y_label] + [info['label'] for key, info in mappings.items() if key.startswith('y_bar_series_') and 'label' in info]
                    valid_y_series = [label for label in y_series_labels if label in df.columns]
                    if x_label and x_label in df.columns and valid_y_series:
                        df_long = df.melt(id_vars=[x_label], value_vars=valid_y_series, var_name='Series', value_name='Value')
                        fig = px.bar(df_long, x=x_label, y='Value', color='Series', barmode='group', title=kpi_name)
                else:
                    if x_label and y_label and x_label in df.columns and y_label in df.columns:
                        fig = px.bar(df, x=x_label, y=y_label, title=kpi_name)

            elif viz_type == "Pie Chart":
                label_col = mappings.get("pie_label", {}).get("label")
                value_col = mappings.get("pie_value", {}).get("label")
                if label_col and value_col and label_col in df.columns and value_col in df.columns:
                    fig = px.pie(df, names=label_col, values=value_col, title=kpi_name)

            elif viz_type == "Box Chart":
                group_col = mappings.get("box_group", {}).get("label")
                value_col = mappings.get("box_value", {}).get("label")
                if group_col and value_col and group_col in df.columns and value_col in df.columns:
                    fig = px.box(df, x=group_col, y=value_col, title=kpi_name)

            elif viz_type == "Heat Map":
                x_label = mappings.get("heat_x", {}).get("label")
                y_label = mappings.get("heat_y", {}).get("label")
                value_col = mappings.get("heat_value", {}).get("label")
                if x_label and y_label and value_col and x_label in df.columns and y_label in df.columns and value_col in df.columns:
                    # Pivot data for heatmap
                    pivot_df = df.pivot(index=y_label, columns=x_label, values=value_col)
                    fig = go.Figure(data=go.Heatmap(
                        z=pivot_df.values,
                        x=pivot_df.columns,
                        y=pivot_df.index,
                        colorscale='Viridis'))
                    fig.update_layout(title=kpi_name, xaxis_title=x_label, yaxis_title=y_label)

            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"Could not generate chart for '{kpi_name}'. Please check data and KPI definition.")

        except Exception as e:
            st.error(f"An error occurred while creating the chart for '{kpi_name}': {e}")
        
        # Increment column index for the next KPI
        col_idx += 1

