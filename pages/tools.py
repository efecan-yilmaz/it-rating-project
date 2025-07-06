import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.utils import JSON_FILE_PATH, load_tool_data_from_json, export_data_to_json

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

    if tool_name:
        new_row = {
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
    else:
        st.toast("Tool name cannot be empty.")

col1, col2, col3, col4, col5 = st.columns(5)

st.markdown("""
    <style>
        div[data-testid="stHint"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
col1.text_input("Tool name", key="tool_name_input")
col2.multiselect("Communication", ["Text chatting", "Conducting Video calls/conferencing", "Sharing - Calendars", "Sharing - Screens", "Sharing - Locations", "Sending Email", "Commenting on Artefacts", "Providing Status updates"], key="cat1_select")
col3.multiselect("Data- & Knowledge Management", ["Searching - (Filtering) Information", "Curating and Organizing Content", "Sharing - Branch Data", "User Profile", "Categorizing and Tagging - Data/Information/Knowledge", "Synchronous, simultaneous editing", "Versioning Data", "Transforming Data", "Archiving Data", "Back Up Data", "Using Forums/discussion boards", "Submitting Ideas", "Rating - Ideas", "Categorizing and Tagging - Ideas", "Tracking Idea Progress", "Customizing Idea Management Workflow", "Creating multiple Projects", "Brainstorming Ideas", "Allocating product data (CAE data etc.)", "Allocating Bill of Materials (BoM)", "Managing Productworkflow and Processes", "Versioning and change tracking for technical documents and product data", "Establishing common language (Glossar tc.)", "Establishing Q&A document", "API Access", "Online Access", "Assigning access rights", "Authentification"], key="cat2_select")
col4.multiselect("Project Management", ["Informing about Leave and Absences", "Delegating Tasks and Follow-up Tracking", "Assining Resources", "Reviewing - tasks", "Working in multiple Projects", "Planning and Scheduling Changes", "Collecting Feedback", "Data analysis - impact analysis", "Visualizing Data", "Sharing - Report", "Conducting Surveys and Polls", "Searching (Filtering) Information- Query", "Data analysis", "Data modelling", "Reporting - Problem (Ticket System, etc)", "Reporting - via dashboards"], key="cat3_select")
col5.multiselect("Product Design", ["Developing solution options", "Rating - solution options", "Assess feasibility", "Sharing - Designs", "Performing numerical analysis", "Designing - 3D Modells and Assemblies", "Rendering and Visualizing Products", "Simulating Designs", "Preparing Prototypes", "Integrating Designs with Manufacturing Processes", "Using AR/VR environments", "Customizing User Interface and Ease of Use", "Gathering and defining requirements", "Negotiate product development contract", "Prioritising requirements", "Tracing requirements", "Validating requirements (Align results with stakeholders)", "Writing Lasten-/Pflichtenheft", "Create system architecture", "Open and view Designs", "Providing Feedback", "Review - Status Updates (Approval, Revision…)", "Designing - 2D Models and Assemblies"], key="cat4_select")

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
            "Category1": st.column_config.ListColumn("Communication"),
            "Category2": st.column_config.ListColumn("Data- & Knowledge Management"),
            "Category3": st.column_config.ListColumn("Project Management"),
            "Category4": st.column_config.ListColumn("Product Design"),
        },
    )

st.header("IT Tools Fishbone Diagram")

def create_fishbone_diagram(df):
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            annotations=[dict(text="No data to display", xref="paper", yref="paper", showarrow=False, font=dict(size=20))]
        )
        return fig

    fig = go.Figure()

    # Parameters for fishbone
    spine_start_x = 0
    spine_end_x = 10
    spine_y = 0
    bone_vertical_offset = 2  # How far bones go up/down from spine
    bone_horizontal_projection = 1.5 # How far bones project horizontally from their spine attachment point

    # 1. Spine
    fig.add_trace(go.Scatter(
        x=[spine_start_x, spine_end_x],
        y=[spine_y, spine_y],
        mode='lines',
        line=dict(color='black', width=3),
        hoverinfo='none'
    ))

    # 2. Head of the fish (Effect/Problem)
    fig.add_trace(go.Scatter(
        x=[spine_end_x], 
        y=[spine_y],
        mode='markers+text',
        marker=dict(symbol='triangle-right', size=20, color='black'),
        text=[" <b>IT Tool Landscape</b>"], # Space for padding from marker
        textposition="middle right", 
        textfont=dict(size=14, color="black"),
        hoverinfo='none'
    ))

    num_tools = len(df)
    # Distribute attachment points along the spine
    # Attach tools between 5% and 65% of the spine length to leave room for the head text and avoid crowding
    attach_zone_start_x = spine_start_x + (spine_end_x - spine_start_x) * 0.05
    attach_zone_end_x = spine_end_x - (spine_end_x - spine_start_x) * 0.35 # End attachment well before head

    if num_tools > 0:
        if num_tools == 1:
            # Center the single tool in the attachment zone
            x_attach_points = [attach_zone_start_x + (attach_zone_end_x - attach_zone_start_x) / 2]
        else:
            # Spread tools across the available zone
            x_attach_points = [attach_zone_start_x + i * (attach_zone_end_x - attach_zone_start_x) / (num_tools - 1) for i in range(num_tools)]
    else:
        x_attach_points = []

    max_abs_y_coord = bone_vertical_offset # For y-axis range setting

    for i, row in df.iterrows():
        tool_name = row["Tool Name"]
        
        categories_list = []
        for cat_col in ["Category1", "Category2", "Category3", "Category4"]:
            cat_data = row[cat_col] # This is a list from st.multiselect
            if isinstance(cat_data, list):
                categories_list.extend(cat_data)
            # Fallback for robustness, though multiselect always gives a list
            elif pd.notna(cat_data) and cat_data: 
                 categories_list.append(str(cat_data))
        
        categories_str = "<br>".join(categories_list)
        
        label_text = f"<b>{tool_name}</b><br>{categories_str if categories_str else '<i>No Categories</i>'}"

        x_attach = x_attach_points[i]
        # Alternate bones: top-right, bottom-right from the spine
        y_bone_tip = bone_vertical_offset if i % 2 == 0 else -bone_vertical_offset
        x_bone_tip = x_attach + bone_horizontal_projection 

        # Draw the bone line
        fig.add_trace(go.Scatter(
            x=[x_attach, x_bone_tip], y=[spine_y, y_bone_tip],
            mode='lines', line=dict(color='dimgray', width=1.5), hoverinfo='none'
        ))

        # Add tool label at the end of the bone
        text_align_vertical = "bottom" if y_bone_tip > 0 else "top" # Aligns text relative to marker
        fig.add_trace(go.Scatter(
            x=[x_bone_tip], y=[y_bone_tip], mode='markers+text',
            marker=dict(size=7, color='royalblue'), text=[label_text],
            textposition=f"{text_align_vertical} right", # Text to the right of marker, aligned by top/bottom
            hoverinfo='text', hovertext=[label_text], textfont=dict(size=10)
        ))

    # Layout adjustments for the fishbone appearance
    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, visible=False, 
                   range=[spine_start_x - 0.5, spine_end_x + bone_horizontal_projection + 4.5]), # Increased range for text
        yaxis=dict(showgrid=False, zeroline=False, visible=False, 
                   range=[-max_abs_y_coord -1.5, max_abs_y_coord + 1.5]), # Symmetrical padding for y-axis
        margin=dict(l=10, r=10, t=10, b=10), # Minimal margins
        plot_bgcolor='rgba(0,0,0,0)' # Transparent background
    )
    return fig

if 'tool_data_df' in st.session_state and not st.session_state.tool_data_df.empty:
    fishbone_fig = create_fishbone_diagram(st.session_state.tool_data_df)
    st.plotly_chart(fishbone_fig, use_container_width=True)
else:
    st.info("Add tools to see the fishbone diagram.")
