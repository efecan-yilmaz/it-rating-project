from utils.utils import (JSON_MANUAL_TASKS_PATH, JSON_DETAILS_DATA_PATH, JSON_USER_RATINGS_PATH, JSON_RE_DETAILS_DATA_PATH)
import os
import streamlit.components.v1 as components

def determine_page():
    if os.path.exists(JSON_RE_DETAILS_DATA_PATH):
        return "pages/requirement_engineering.py"
    elif os.path.exists(JSON_USER_RATINGS_PATH):
        return "pages/user_ratings.py"
    elif os.path.exists(JSON_DETAILS_DATA_PATH):
        return "pages/detail_data.py"
    elif os.path.exists(JSON_MANUAL_TASKS_PATH):
        return "pages/manual_tasks.py"
    return "pages/tools.py"


def hide_hidden_header_and_list_items():
    """
    Injects JavaScript to hide the <header> element with innerHTML 'hidden'
    and all subsequent <li> elements in the DOM, always running on the top window.
    Runs immediately and then every 200ms.
    """
    components.html("""
    <script>
    function hideHeadersAndListItems() {
        const headers = window.top.document.querySelectorAll('header');
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
    }
    hideHeadersAndListItems();
    setInterval(hideHeadersAndListItems, 200);
    </script>
    """, height=0)