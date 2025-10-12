import pandas as pd
import streamlit as st
import json

JSON_FILE_PATH = "data/tool_data.json"
JSON_MANUAL_TASKS_PATH = "data/manual_tasks_data.json"
JSON_DETAILS_DATA_PATH = "data/details_data.json"
JSON_RE_DETAILS_DATA_PATH = "data/re_details_data.json"
JSON_PRIO_DATA_PATH = "data/priority_data.json"
JSON_USER_RATINGS_PATH = "data/user_ratings.json"
TEMPLATE_PATH = "data/METIS_VoC.xlsx"
DEF_TOOLS_DATA_PATH = "data/def_tools_data.xlsx"
JSON_SELECTED_USE_CASE_PATH = "data/selected_use_case.json"
JSON_DEFAULT_USE_CASES_PATH = "data/default_use_cases.json"

def load_def_tools_data_from_xlsx(file_path=DEF_TOOLS_DATA_PATH) -> dict:
    """
    Reads the first sheet of the given XLSX file and returns a dictionary:
    {tool_id: {"activities": [{"activity": <string>, "category": <string>}, ...], "automation": <number>, "ai_level": <number>, "syncronization": <number>,
               "integration": <value>, "usability": <value>, "cost": <value>, "support": <value>, "payment_method": <list of strings>}}
    Also reads the second sheet for automation, ai_level, syncronization, integration, usability, cost, support, and payment_method values.
    """
    # First sheet: activities and categories
    df = pd.read_excel(file_path, sheet_name=0, header=None)
    tool_ids = df.iloc[0, 3:92].tolist()  # D to CM
    activity_names = df.iloc[1:, 2].tolist()  # C, from row 2
    category_names = df.iloc[1:, 1].tolist()  # B, from row 2
    data = df.iloc[1:, 3:92]

    result = {}
    for col_idx, tool_id in enumerate(tool_ids):
        if pd.isna(tool_id):
            continue
        activities = []
        for row_idx, val in enumerate(data.iloc[:, col_idx]):
            if val == 1:
                activity = activity_names[row_idx]
                category = category_names[row_idx]
                if pd.notna(activity) and pd.notna(category):
                    activities.append({"activity": activity, "category": category})
        result[str(tool_id)] = {"activities": activities}

    # Second sheet: automation, ai_level, syncronization, integration, usability, cost, support, payment_method
    df2 = pd.read_excel(file_path, sheet_name=1, header=None)
    for idx in range(1, df2.shape[0]):
        tool_name = df2.iloc[idx, 0]
        if pd.isna(tool_name):
            continue
        tool_name_lc = str(tool_name).strip().lower()
        # Find matching tool in result (case-insensitive)
        for key in result:
            if str(key).strip().lower() == tool_name_lc:
                # Columns: B=1, C=2, D=3, E=4, F=5, I=8, J=9, K=10, L=11
                integration = df2.iloc[idx, 1]
                usability = df2.iloc[idx, 2]
                cost = df2.iloc[idx, 3]
                support = df2.iloc[idx, 4]
                functionality = df2.iloc[idx, 5]  # Column F
                automation = df2.iloc[idx, 8]
                ai_level = df2.iloc[idx, 9]
                syncronization = df2.iloc[idx, 10]
                payment_method_raw = df2.iloc[idx, 11]  # Column L
                if pd.notna(integration):
                    result[key]["integration"] = integration
                if pd.notna(usability):
                    result[key]["usability"] = usability
                if pd.notna(cost):
                    result[key]["cost"] = cost
                if pd.notna(support):
                    result[key]["support"] = support
                if pd.notna(functionality):
                    result[key]["functionality"] = functionality
                if pd.notna(automation):
                    result[key]["automation"] = automation
                if pd.notna(ai_level):
                    result[key]["ai_level"] = ai_level
                if pd.notna(syncronization):
                    result[key]["syncronization"] = syncronization
                if pd.notna(payment_method_raw):
                    # Split by "/", trim, and filter out empty strings
                    if str(payment_method_raw).strip() == "-":
                        payment_methods = [0]
                    else:
                        payment_methods = [int(pm.strip()) for pm in str(payment_method_raw).split("/") if pm.strip()]
                    result[key]["payment_method"] = payment_methods
                break  # Stop after first match

    return result

def load_tool_data_from_json(file_path: str) -> pd.DataFrame:
    default_columns = ["Tool Name", "ID", "Category1", "Category2", "Category3", "Category4"]
    try:
        df = pd.read_json(file_path, orient='records', dtype=False)
        # Ensure all necessary columns exist, add them if they don't
        for col in default_columns:
            if col not in df.columns:
                df[col] = [[] if "Category" in col else "" for _ in range(len(df))]
        # Ensure correct column order and fill NaNs appropriately
        df = df.reindex(columns=default_columns)
        for col in ["Category1", "Category2", "Category3", "Category4"]:
            # Ensure category columns are lists, handling potential NaNs from reindex or initial load
            df[col] = df[col].apply(lambda x: x if isinstance(x, list) else ([] if pd.isna(x) else [x]))
        return df
    except FileNotFoundError:
        st.toast(f"'{file_path}' not found. Starting with an empty tool list.")
        return pd.DataFrame(columns=default_columns)
    except ValueError as e: # Handles empty or malformed JSON
        st.toast(f"Could not decode JSON from '{file_path}'. It might be empty or malformed. Error: {e}. Starting with an empty tool list.")
        return pd.DataFrame(columns=default_columns)
    except Exception as e:
        st.toast(f"An unexpected error occurred while loading '{file_path}': {e}. Starting with an empty tool list.")
        return pd.DataFrame(columns=default_columns)

def load_manual_task_data_from_json(file_path: str) -> pd.DataFrame:
    default_columns = ["CategoryGroup", "CategoryName", "ID"]
    try:
        df = pd.read_json(file_path, orient="records", dtype=False)
        for col in default_columns:
            if col not in df.columns:
                df[col] = ""
        df = df.reindex(columns=default_columns)
        return df
    except FileNotFoundError:
        st.toast(f"'{file_path}' not found. Starting with an empty manual task list.")
        return pd.DataFrame(columns=default_columns)
    except ValueError as e:
        st.toast(f"Could not decode JSON from '{file_path}'. It might be empty or malformed. Error: {e}. Starting with an empty manual task list.")
        return pd.DataFrame(columns=default_columns)
    except Exception as e:
        st.toast(f"An unexpected error occurred while loading '{file_path}': {e}. Starting with an empty manual task list.")
        return pd.DataFrame(columns=default_columns)

def load_details_data_from_json(file_path: str) -> pd.DataFrame:
    """Loads the details data from a JSON file."""
    try:
        df = pd.read_json(file_path, orient='records', dtype=False)
        return df
    except (FileNotFoundError, ValueError):
        # Return empty df if file not found or empty/malformed
        return pd.DataFrame()

def export_data_to_json(df: pd.DataFrame, file_path: str):
    """Generic function to export a DataFrame to a JSON file."""
    if not isinstance(df, pd.DataFrame):
        st.toast(f"Error: Data to save is not a DataFrame.")
        return
    try:
        df.to_json(file_path, orient="records", indent=4, force_ascii=False)
        # st.toast(f"Data saved to {file_path}", icon="💾") # Optional: uncomment for save confirmation
    except Exception as e:
        st.toast(f"Error while saving data to '{file_path}': {e}")

def load_from_json(file_path):
    """
    Loads the default use case from the specified JSON file.
    Returns the content as a dictionary.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.toast(f"'{file_path}' not found. Returning empty dictionary.")
        return {}
    except json.JSONDecodeError as e:
        st.toast(f"Could not decode JSON from '{file_path}': {e}. Returning empty dictionary.")
        return {}
    except Exception as e:
        st.toast(f"An unexpected error occurred while loading '{file_path}': {e}. Returning empty dictionary.")
        return {}