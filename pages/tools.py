import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import uuid
from utils.utils import (JSON_FILE_PATH, load_tool_data_from_json, export_data_to_json)
from data.SelectValues import (Category1Options, Category2Options, Category3Options, Category4Options)

# Initialize the DataFrame in session state if it doesn't exist
if 'tool_data_df' not in st.session_state:
    st.session_state.tool_data_df = load_tool_data_from_json(JSON_FILE_PATH)

if "tool_name_input" not in st.session_state:
    st.session_state.tool_name_input = ""
if "cat1_select" not in st.session_state:
    st.session_state.cat1_select = []
if "cat2_select" not in st.session_state:
    st.session_state.cat2_select = []
if "cat3_select" not in st.session_state:
    st.session_state.cat3_select = []
if "cat4_select" not in st.session_state:
    st.session_state.cat4_select = []

st.title("IT Tool Data Collection")
st.write("Please enter your IT tools and select related catagories")

st.header("New Data")

def add_tool_callback():
    tool_name = st.session_state.tool_name_input
    category1 = st.session_state.cat1_select
    category2 = st.session_state.cat2_select
    category3 = st.session_state.cat3_select
    category4 = st.session_state.cat4_select

    if not tool_name:
        st.toast("Tool name cannot be empty.")
        return

    if not (category1 or category2 or category3 or category4):
        st.toast("Please select at least one category.")
        return

    new_row = {
        "ID": str(uuid.uuid4()),  # Add unique ID
        "Tool Name": tool_name,
        "Category1": category1,
        "Category2": category2,
        "Category3": category3,
        "Category4": category4
    }
    new_row_df = pd.DataFrame([new_row])
    st.session_state.tool_data_df = pd.concat([st.session_state.tool_data_df, new_row_df], ignore_index=True)
    export_data_to_json(st.session_state.tool_data_df, JSON_FILE_PATH)
    st.toast(f"Tool '{tool_name}' added successfully!")
    st.session_state.tool_name_input = ""
    st.session_state.cat1_select = []
    st.session_state.cat2_select = []
    st.session_state.cat3_select = []
    st.session_state.cat4_select = []

col1, col2, col3, col4, col5 = st.columns(5)

st.markdown("""
    <style>
        div[data-testid="stHint"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
col1.text_input("Tool name", key="tool_name_input")
col2.multiselect("Communication", sorted(Category1Options), key="cat1_select")
col3.multiselect("Data- & Knowledge Management", sorted(Category2Options), key="cat2_select")
col4.multiselect("Project Management", sorted(Category3Options), key="cat3_select")
col5.multiselect("Product Design", sorted(Category4Options), key="cat4_select")

st.button("➕ Add", on_click=add_tool_callback)

st.header("Tool List")

def on_table_selection(): () # necessary for dataframe to show the line selection

def delete_from_table():
    current_df = st.session_state.tool_data_df
    st.session_state.tool_data_df = current_df.drop(st.session_state.tool_data_df_edit.selection.rows).reset_index(drop=True)
    export_data_to_json(st.session_state.tool_data_df, JSON_FILE_PATH)
    st.toast("Selected tool(s) deleted.")

if st.session_state.tool_data_df.empty:
    st.info("No tools added yet. Use the form above to add your first tool.")
else:
    st.button("🗑️ Delete Selected", on_click=delete_from_table)
    st.dataframe(
        st.session_state.tool_data_df,
        selection_mode="multi-row",
        on_select=on_table_selection,
        key="tool_data_df_edit",
        column_config={
            "ID": None,  # Hide the ID column
            "Category1": st.column_config.ListColumn("Communication"),
            "Category2": st.column_config.ListColumn("Data- & Knowledge Management"),
            "Category3": st.column_config.ListColumn("Project Management"),
            "Category4": st.column_config.ListColumn("Product Design"),
        },
    )

st.header("IT Tools Fishbone Diagram")

def group_tools_by_category(df):
    category_map = {
        "Category1": "Communication",
        "Category2": "Data- & Knowledge Management",
        "Category3": "Project Management",
        "Category4": "Product Design"
    }
    grouped = {v: {} for v in category_map.values()}
    for _, row in df.iterrows():
        tool_name = row["Tool Name"]
        for cat_col, cat_name in category_map.items():
            values = row[cat_col]
            if isinstance(values, list):
                for v in values:
                    grouped[cat_name].setdefault(v, []).append(tool_name)  # Only tool name
    return grouped

def create_fishbone_diagram_grouped(df):
    grouped = group_tools_by_category(df)
    fig = go.Figure()

    # Fishbone spine
    spine_start_x = 0
    spine_end_x = 10
    spine_y = 0
    fig.add_trace(go.Scatter(
        x=[spine_start_x, spine_end_x],
        y=[spine_y, spine_y],
        mode='lines',
        line=dict(color='black', width=3),
        hoverinfo='none'
    ))

    # Fish head
    fig.add_trace(go.Scatter(
        x=[spine_end_x],
        y=[spine_y],
        mode='markers+text',
        marker=dict(symbol='triangle-right', size=20, color='black'),
        text=[" <b>IT Tool Landscape</b>"],
        textposition="middle right",
        textfont=dict(size=14, color="black"),
        hoverinfo='none'
    ))

    # Attach categories to the spine
    categories = list(grouped.keys())
    n_cat = len(categories)
    attach_zone_start_x = spine_start_x + (spine_end_x - spine_start_x) * 0.1
    attach_zone_end_x = spine_end_x - (spine_end_x - spine_start_x) * 0.25
    x_attach_points = [
        attach_zone_start_x + i * (attach_zone_end_x - attach_zone_start_x) / (n_cat - 1)
        for i in range(n_cat)
    ]
    bone_vertical_offset = 2.5
    bone_horizontal_projection = 2.5

    for i, (cat, values_dict) in enumerate(grouped.items()):
        x_attach = x_attach_points[i]
        y_bone_tip = bone_vertical_offset if i % 2 == 0 else -bone_vertical_offset
        x_bone_tip = x_attach + bone_horizontal_projection

        # Draw bone
        fig.add_trace(go.Scatter(
            x=[x_attach, x_bone_tip], y=[spine_y, y_bone_tip],
            mode='lines', line=dict(color='dimgray', width=2), hoverinfo='none'
        ))

        # Compose label: category + entries
        entries = []
        for value, tools in values_dict.items():
            entries.append(f"{value} | {', '.join(tools)}")
        label_text = f"<b>{cat}</b><br>" + "<br>".join(entries) if entries else f"<b>{cat}</b><br><i>No entries</i>"

        text_align_vertical = "bottom" if y_bone_tip > 0 else "top"
        fig.add_trace(go.Scatter(
            x=[x_bone_tip], y=[y_bone_tip], mode='markers+text',
            marker=dict(size=10, color='royalblue'),
            text=[label_text],
            textposition=f"{text_align_vertical} right",
            hoverinfo='text', hovertext=[label_text], textfont=dict(size=11)
        ))

    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, visible=False,
                   range=[spine_start_x - 0.5, spine_end_x + bone_horizontal_projection + 4.5]),
        yaxis=dict(showgrid=False, zeroline=False, visible=False,
                   range=[-bone_vertical_offset - 2, bone_vertical_offset + 2]),
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

if 'tool_data_df' in st.session_state and not st.session_state.tool_data_df.empty:
    fishbone_fig = create_fishbone_diagram_grouped(st.session_state.tool_data_df)
    st.plotly_chart(fishbone_fig, use_container_width=True)
else:
    st.info("Add tools to see the fishbone diagram.")
