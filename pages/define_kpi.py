import streamlit as st
from data.SelectValues import KPITypeOptions, VisualizationMethodOptions
import json
import uuid
from pathlib import Path

st.title("Define KPI")
st.write("Define your Key Performance Indicators (KPIs) for selected tools and manual tasks.")

# storage path (project-relative)
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "kpi"
DATA_DIR.mkdir(parents=True, exist_ok=True)
KPI_FILE = DATA_DIR / "kpi_defs.json"

def load_kpis():
    if KPI_FILE.exists():
        try:
            with KPI_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_kpis(kpis):
    with KPI_FILE.open("w", encoding="utf-8") as f:
        json.dump(kpis, f, indent=2, ensure_ascii=False)

# initialize session storage for kpis
if "kpi_defs" not in st.session_state:
    st.session_state["kpi_defs"] = load_kpis()

# --- replaced: handle edit/clear BEFORE widgets are created ---
# If an edit was requested previously, populate widget keys BEFORE widgets are created.
# Use a pending payload and always set the widget keys now (this is before widgets are instantiated).
if "editing_pending" in st.session_state:
    pending = st.session_state.pop("editing_pending")
    st.session_state["editing_id"] = pending.get("id")
    st.session_state["kpi_name_input"] = pending.get("name", "")
    st.session_state["visualization_method_select"] = pending.get("visualization", "")
    st.session_state["measurement_responsible_input"] = pending.get("measurement_responsible", "")
    for prefix, info in pending.get("mappings", {}).items():
        if "label" in info:
            st.session_state[f"{prefix}_label"] = info["label"]
        if "type" in info:
            st.session_state[f"{prefix}_type"] = info["type"]
    for key in ("multiline_series_count", "bar_grouped", "bar_group_count"):
        if key in pending:
            st.session_state[key] = pending[key]

# If a save requested clearing the form, perform the clear now (before widgets are created)
if "clear_form" in st.session_state:
    for key in ("kpi_name_input", "measurement_responsible_input", "visualization_method_select"):
        st.session_state[key] = ""
    st.session_state.pop("clear_form", None)

col1, col2, col3 = st.columns([1, 1, 1])

# Provide initial values from session_state so widgets don't get overwritten later.
col1.text_input("KPI Name", value=st.session_state.get("kpi_name_input", ""), key="kpi_name_input")

visualization_method = col1.selectbox(
    "Visualization Method",
    VisualizationMethodOptions,
    index=(VisualizationMethodOptions.index(st.session_state.get("visualization_method_select"))
           if st.session_state.get("visualization_method_select") in VisualizationMethodOptions else 0),
    key="visualization_method_select"
)

col1.text_input("Measurement Responsible",
                value=st.session_state.get("measurement_responsible_input", ""),
                key="measurement_responsible_input")

def axis_input(row_label, key_prefix, data_types=("Numeric", "Date", "Text"), cols=(1,1,3)):
    c1, c2, c3 = st.columns(cols)
    c1.text_input(row_label, key=f"{key_prefix}_label")
    c2.selectbox("Data Type", list(data_types), key=f"{key_prefix}_type")

st.markdown("### Data mapping for the selected visualization")
st.caption(f"Best-practice mappings for: {visualization_method}")

if visualization_method == "Line Chart":
    st.info("Line chart: typically one continuous x-axis (time or numeric) and one numeric y series.")
    axis_input("x (e.g. Time / Date)", "x", data_types=("Date", "Numeric", "Text"))
    axis_input("y (numeric value)", "y", data_types=("Numeric",))

elif visualization_method == "Multi-Line Chart":
    st.info("Multi-line: one shared x-axis (time/ordinal) and multiple numeric series (legended).")
    axis_input("x (shared axis, e.g. Time)", "x", data_types=("Date", "Numeric", "Text"))
    series_count = st.slider("Number of series", 2, 10, 3, key="multiline_series_count")
    for i in range(1, series_count + 1):
        axis_input(f"y{i} (series {i} name)", f"y_series_{i}", data_types=("Numeric",))

elif visualization_method == "Bar Chart":
    st.info("Bar chart: categorical x and numeric y. For grouped bars, add extra series.")
    axis_input("x (category)", "x", data_types=("Text", "Numeric"))
    axis_input("y (value)", "y", data_types=("Numeric",))
    grouped = st.checkbox("Grouped bars (multiple series)?", key="bar_grouped")
    if grouped:
        group_count = st.slider("Number of bar series", 2, 6, 2, key="bar_group_count")
        for i in range(2, group_count + 1):
            axis_input(f"y{i} (series {i} value)", f"y_bar_series_{i}", data_types=("Numeric",))

elif visualization_method == "Pie Chart":
    st.info("Pie chart: one categorical label and one numeric value per slice.")
    axis_input("Category label", "pie_label", data_types=("Text",))
    axis_input("Value (numeric)", "pie_value", data_types=("Numeric",))

elif visualization_method == "Box Chart":
    st.info("Box chart: one numeric variable and optional grouping (category) for multiple boxes.")
    axis_input("Grouping (category)", "box_group", data_types=("Text",))
    axis_input("Numeric value (distribution)", "box_value", data_types=("Numeric",))

elif visualization_method == "Heat Map":
    st.info("Heat map: two categorical/ordinal axes and a numeric intensity/value.")
    axis_input("x (category / column)", "heat_x", data_types=("Text", "Numeric"))
    axis_input("y (category / row)", "heat_y", data_types=("Text", "Numeric"))
    axis_input("Value (intensity)", "heat_value", data_types=("Numeric",))

else:
    st.write("Select a visualization method to see required data mappings.")

def gather_inputs():
    kpi = {
        "id": None,
        "name": st.session_state.get("kpi_name_input", ""),
        "visualization": st.session_state.get("visualization_method_select", ""),
        "measurement_responsible": st.session_state.get("measurement_responsible_input", ""),
        "mappings": {}
    }
    # collect label/type pairs without regex by checking suffixes
    for key, val in st.session_state.items():
        if key.endswith("_label"):
            prefix = key[:-6]  # remove "_label"
            if prefix not in kpi["mappings"]:
                kpi["mappings"][prefix] = {}
            kpi["mappings"][prefix]["label"] = val
        elif key.endswith("_type"):
            prefix = key[:-5]  # remove "_type"
            if prefix not in kpi["mappings"]:
                kpi["mappings"][prefix] = {}
            kpi["mappings"][prefix]["type"] = val
    # include other UI state keys if present
    for optional in ("multiline_series_count", "bar_grouped", "bar_group_count"):
        if optional in st.session_state:
            kpi[optional] = st.session_state[optional]
    return kpi

def add_kpi(kpi):
    kpi["id"] = uuid.uuid4().hex
    st.session_state["kpi_defs"].append(kpi)
    save_kpis(st.session_state["kpi_defs"])

def update_kpi(kpi_id, kpi):
    for i, item in enumerate(st.session_state["kpi_defs"]):
        if item.get("id") == kpi_id:
            kpi["id"] = kpi_id
            st.session_state["kpi_defs"][i] = kpi
            save_kpis(st.session_state["kpi_defs"])
            return

def delete_kpi(kpi_id):
    st.session_state["kpi_defs"] = [k for k in st.session_state["kpi_defs"] if k.get("id") != kpi_id]
    save_kpis(st.session_state["kpi_defs"])

editing_id = st.session_state.get("editing_id")

save_label = "💾 Update KPI" if editing_id else "💾 Save KPI"
# Disable saving new KPIs if the limit of 6 is reached.
save_disabled = not editing_id and len(st.session_state.get("kpi_defs", [])) >= 6

if save_disabled:
    st.warning("You have reached the maximum of 6 KPIs. To add a new one, please delete an existing KPI.")

if st.button(save_label, key="save_kpi_button", disabled=save_disabled):
    kpi = gather_inputs()
    if editing_id:
        update_kpi(editing_id, kpi)
        st.success("KPI updated.")
        del st.session_state["editing_id"]
    else:
        add_kpi(kpi)
        st.success("KPI saved.")
    # request main form clear on next run (perform clearing before widgets are created)
    st.session_state["clear_form"] = True
    # reload kpis into session and rerun so the cleared values take effect
    st.session_state["kpi_defs"] = load_kpis()
    st.rerun()

st.markdown("### Saved KPIs")
kpis = st.session_state.get("kpi_defs", [])
if kpis:
    # Prepare data for the dataframe
    df_rows = []
    for k in kpis:
        mappings = k.get("mappings", {})
        details = []
        if mappings:
            for prefix, info in mappings.items():
                label = info.get("label", "")
                dtype = info.get("type", "")
                if label and dtype:
                    details.append(f"{prefix}: {label} ({dtype})")
                elif label:
                    details.append(f"{prefix}: {label}")
                else:
                    details.append(f"{prefix}")
            mapping_str = ", ".join(details)
        else:
            mapping_str = ""
        df_rows.append({
            "id": k.get("id"),
            "Name": k.get("name"),
            "Visualization": k.get("visualization"),
            "Measurement Responsible": k.get("measurement_responsible"),
            "Mappings": mapping_str
        })

    # Display the dataframe with single-row selection
    selection = st.dataframe(
        df_rows,
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True,
        column_config={"id": None},  # Hide the ID column from view
        key="kpi_selection"
    )

    # Get the selected row's data if a selection was made
    selected_kpi = None
    if selection.selection.rows:
        selected_row_index = selection.selection.rows[0]
        selected_kpi_id = df_rows[selected_row_index]["id"]
        # Find the full KPI object from the original list
        selected_kpi = next((k for k in kpis if k["id"] == selected_kpi_id), None)

    # Add Edit and Delete buttons, disabled if nothing is selected
    col1, col2, _ = st.columns([1, 1, 5])
    edit_disabled = not selected_kpi
    delete_disabled = not selected_kpi

    if col1.button("Edit Selected", disabled=edit_disabled):
        if selected_kpi:
            st.session_state["editing_pending"] = selected_kpi
            st.session_state["editing_id"] = selected_kpi["id"]
            st.rerun()

    if col2.button("Delete Selected", disabled=delete_disabled):
        if selected_kpi:
            delete_kpi(selected_kpi["id"])
            st.warning("KPI deleted.")
            st.rerun()
else:
    st.write("No KPIs defined yet. Use the form above to add one.")