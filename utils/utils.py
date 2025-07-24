import pandas as pd
import streamlit as st

JSON_FILE_PATH = "data/tool_data.json"
JSON_MANUAL_TASKS_PATH = "data/manual_tasks_data.json"
JSON_DETAILS_DATA_PATH = "data/details_data.json"
JSON_RE_DETAILS_DATA_PATH = "data/re_details_data.json"
JSON_PRIO_DATA_PATH = "data/priority_data.json"
JSON_USER_RATINGS_PATH = "data/user_ratings.json"
TEMPLATE_PATH = "data/METIS_VoC.xlsx"

def load_tool_data_from_json(file_path: str) -> pd.DataFrame:
    default_columns = ["Tool Name", "Category1", "Category2", "Category3", "Category4"]
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
    default_columns = ["CategoryGroup", "CategoryName"]
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