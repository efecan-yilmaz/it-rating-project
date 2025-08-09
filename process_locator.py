def hide_hidden_header_and_list_items():
    """
    Injects JavaScript to hide the <header> element with innerHTML 'hidden'
    and all subsequent <li> elements in the DOM.
    """
    import streamlit.components.v1 as components
    components.html("""
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        const headers = document.querySelectorAll('header');
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
    });
    </script>
    """,