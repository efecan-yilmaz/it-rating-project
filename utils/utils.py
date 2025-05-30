import pandas as pd
import streamlit as st

JSON_FILE_PATH = "tool_data.json"

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