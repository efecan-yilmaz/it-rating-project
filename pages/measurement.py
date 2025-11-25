import streamlit as st
import json
from pathlib import Path
import pandas as pd

st.title("Measurement")
st.write("Enter the measurement data for the defined KPIs.")

# --- Data Loading and Saving ---
BASE_DIR = Path(__file__).resolve().parent.parent
KPI_DEFS_FILE = BASE_DIR / "data" / "kpi" / "kpi_defs.json"
MEASUREMENTS_DIR = BASE_DIR / "data" / "kpi" / "measurements"
MEASUREMENTS_DIR.mkdir(parents=True, exist_ok=True)

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

def save_measurement_data(kpi_id, data):
    """Saves measurement data for a specific KPI ID."""
    measurement_file = MEASUREMENTS_DIR / f"{kpi_id}.json"
    with measurement_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- Main App ---
kpis = load_kpis()

if not kpis:
    st.warning("No KPIs defined yet. Please go to the 'Define KPI' page to create a KPI first.")
    st.stop()

# Create a mapping from KPI name to the full KPI object
kpi_map = {kpi['name']: kpi for kpi in kpis}
kpi_names = list(kpi_map.keys())

# --- KPI Selection ---
selected_kpi_name = st.selectbox(
    "Select a KPI to enter or view measurement data",
    options=kpi_names,
    index=0,
    key="selected_kpi"
)

if selected_kpi_name:
    selected_kpi = kpi_map[selected_kpi_name]
    kpi_id = selected_kpi["id"]

    # --- Data Entry Form ---
    st.markdown(f"### Enter data for: **{selected_kpi_name}**")
    st.caption(f"Visualization: {selected_kpi['visualization']} | Responsible: {selected_kpi['measurement_responsible']}")

    # Define columns for the data editor based on KPI mappings
    column_config = {}
    for prefix, info in selected_kpi.get("mappings", {}).items():
        if "label" in info and "type" in info:
            label = info["label"]
            dtype = info["type"]
            if dtype == "Date":
                column_config[label] = st.column_config.DatetimeColumn(
                    label,
                    format="YYYY-MM-DD HH:mm",
                    help="Select a date and time"
                )
            elif dtype == "Numeric":
                column_config[label] = st.column_config.NumberColumn(
                    label,
                    help="Enter a number"
                )
            elif dtype == "Text":
                column_config[label] = st.column_config.TextColumn(
                    label,
                    help="Enter text"
                )
    
    # Sort columns to have a consistent order
    sorted_labels = [info["label"] for prefix, info in sorted(selected_kpi.get("mappings", {}).items()) if "label" in info]


    # Load existing data or create an empty DataFrame
    existing_data = load_measurement_data(kpi_id)
    df = pd.DataFrame(existing_data)
    
    # Convert columns to correct dtypes before passing to data_editor
    for prefix, info in selected_kpi.get("mappings", {}).items():
        if "label" in info and "type" in info:
            label = info["label"]
            dtype = info["type"]
            if label in df.columns:
                if dtype == "Date":
                    df[label] = pd.to_datetime(df[label], errors='coerce')
                elif dtype == "Numeric":
                    df[label] = pd.to_numeric(df[label], errors='coerce')

    # Ensure all defined columns exist, even if no data is present
    for label in sorted_labels:
        if label not in df.columns:
            df[label] = None

    # Reorder DataFrame columns to match the sorted labels
    df = df[sorted_labels]

    st.info("You can add, edit, or delete rows directly in the table. To delete a row, select it by clicking its header and press the `Delete` key.")
    
    # Use st.data_editor for interactive data entry
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        hide_index=True,
        column_config=column_config,
        key=f"data_editor_{kpi_id}" # Unique key to reset table on KPI change
    )

    # --- Save/Delete Actions ---
    if st.button("💾 Save Measurements", key="save_measurements"):
        # Create a copy to avoid modifying the displayed DataFrame
        df_to_save = edited_df.copy()

        # Convert datetime columns to ISO 8601 string format for JSON serialization
        for col in df_to_save.select_dtypes(include=['datetime64[ns]']).columns:
            # Using .dt.strftime to format, and handling NaT (Not a Time) values
            df_to_save[col] = df_to_save[col].dt.strftime('%Y-%m-%d %H:%M:%S').replace({pd.NaT: None})

        # Convert DataFrame to list of dicts, dropping rows where all values are None
        output_data = df_to_save.dropna(how='all').to_dict('records')
        save_measurement_data(kpi_id, output_data)
        st.success(f"Measurements for '{selected_kpi_name}' saved successfully.")
        st.rerun()

