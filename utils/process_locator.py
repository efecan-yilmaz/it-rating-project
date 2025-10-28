from utils.utils import (CURRENT_PAGE_JSON, JSON_MANUAL_TASKS_PATH, JSON_SELECTED_USE_CASE_PATH, JSON_DETAILS_DATA_PATH, JSON_USER_RATINGS_PATH, JSON_RE_DETAILS_DATA_PATH, JSON_PRIO_DATA_PATH)
import os
import streamlit.components.v1 as components
from enum import Enum
import json
import streamlit as st

class Page(Enum):
    WELCOME = "pages/welcome.py"
    READY_USE_CASE = "pages/ready_use_case.py"
    TOOLS = "pages/tools.py"
    MANUAL_TASKS = "pages/manual_tasks.py"
    DETAIL_DATA = "pages/detail_data.py"
    USER_RATINGS = "pages/user_ratings.py"
    REQUIREMENT_ENGINEERING = "pages/requirement_engineering.py"
    REQUIREMENT = "pages/requirement.py"

def save_current_page(page: Page):
    with open(CURRENT_PAGE_JSON, "w") as f:
        json.dump({"current_page": page.value}, f)

def read_current_page() -> Page:
    try:
        with open(CURRENT_PAGE_JSON, "r") as f:
            data = json.load(f)
            return Page(data.get("current_page", Page.WELCOME.value))
    except FileNotFoundError:
        return Page.WELCOME

def determine_page():
    current_page = read_current_page().value
    if current_page == Page.WELCOME.value:
        return current_page
    elif current_page == Page.READY_USE_CASE.value:
        if not os.path.exists(JSON_SELECTED_USE_CASE_PATH):
            save_current_page(Page.WELCOME)
            return Page.WELCOME.value
        else:
            return current_page
    elif current_page == Page.TOOLS.value:
        return current_page
    elif current_page == Page.MANUAL_TASKS.value:
        if not os.path.exists(JSON_PRIO_DATA_PATH):
            save_current_page(Page.TOOLS)
            return Page.TOOLS.value
        else:
            save_current_page(Page.MANUAL_TASKS)
            return current_page
    # elif current_page == Page.DETAIL_DATA.value:
    #     if not os.path.exists(JSON_PRIO_DATA_PATH):
    #         save_current_page(Page.TOOLS)
    #         return Page.TOOLS.value
    #     else:
    #         save_current_page(Page.DETAIL_DATA)
    #         return current_page
    elif current_page == Page.USER_RATINGS.value:
        if not os.path.exists(JSON_DETAILS_DATA_PATH):
            save_current_page(Page.DETAIL_DATA)
            return Page.DETAIL_DATA.value
        else:
            save_current_page(Page.USER_RATINGS)
            return current_page
    elif current_page == Page.REQUIREMENT_ENGINEERING.value:
        if not os.path.exists(JSON_DETAILS_DATA_PATH):
            save_current_page(Page.DETAIL_DATA)
            return Page.DETAIL_DATA.value
        else:
            return current_page
    elif current_page == Page.REQUIREMENT.value:
        if not os.path.exists(JSON_RE_DETAILS_DATA_PATH):
            save_current_page(Page.REQUIREMENT_ENGINEERING)
            return Page.REQUIREMENT_ENGINEERING.value
        else:
            return current_page

def run_redirect(default_page=Page.WELCOME.value):
    redirected_page = determine_page()
    if redirected_page and redirected_page != default_page:
        st.switch_page(redirected_page)

def clean_for_previous_direction(page: Page):
    if page == Page.MANUAL_TASKS:
        if os.path.exists(JSON_MANUAL_TASKS_PATH):
            os.remove(JSON_MANUAL_TASKS_PATH)
        if os.path.exists(JSON_DETAILS_DATA_PATH):
            os.remove(JSON_DETAILS_DATA_PATH)
    # elif page == Page.DETAIL_DATA:
    #     if os.path.exists(JSON_DETAILS_DATA_PATH):
    #         os.remove(JSON_DETAILS_DATA_PATH)
    elif page == Page.USER_RATINGS:
        if os.path.exists(JSON_USER_RATINGS_PATH):
            os.remove(JSON_USER_RATINGS_PATH)
    elif page == Page.REQUIREMENT_ENGINEERING:
        if os.path.exists(JSON_RE_DETAILS_DATA_PATH):
            os.remove(JSON_RE_DETAILS_DATA_PATH)

    # if os.path.exists(JSON_RE_DETAILS_DATA_PATH):
    #     return "pages/requirement_engineering.py"
    # elif os.path.exists(JSON_USER_RATINGS_PATH):
    #     return "pages/user_ratings.py"
    # elif os.path.exists(JSON_DETAILS_DATA_PATH):
    #     return "pages/detail_data.py"
    # elif os.path.exists(JSON_MANUAL_TASKS_PATH):
    #     return "pages/manual_tasks.py"
    # return "pages/tools.py"

def hide_hidden_header_and_list_items():
    """
    Injects JavaScript to hide the <header> element with innerHTML 'hidden'
    and all subsequent <li> elements in the DOM, always running on the top window.
    Also hides any <button> elements whose visible text contains "view" (case-insensitive).
    Runs immediately and then every 200ms.
    """
    components.html("""
    <script>
    function hideHeadersListItemsAndViewButtons() {
        const doc = window.top.document;
        const headers = doc.querySelectorAll('header');
        let hide = false;
        headers.forEach(header => {
            if (header.innerHTML.trim() === "hidden") {
                hide = true;
                header.style.display = "none";
            }
            if (hide) {
                let next = header.nextElementSibling;
                while (next && next.tagName === "LI") {
                    next.style.display = "none";
                    next = next.nextElementSibling;
                }
            }
        });

        // Hide any <button> elements whose visible text contains "view" (case-insensitive)
        const buttons = doc.querySelectorAll('button');
        buttons.forEach(btn => {
            try {
                if (btn.innerText && btn.innerText.trim().toLowerCase().includes("view")) {
                    btn.style.display = "none";
                }
            } catch (e) {
                // ignore cross-origin or other access issues
            }
        });
    }
    hideHeadersListItemsAndViewButtons();
    setInterval(hideHeadersListItemsAndViewButtons, 200);
    </script>
    """, height=0)