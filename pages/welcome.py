from narwhals import col
import streamlit as st
from utils.process_locator import save_current_page, Page, run_redirect
from data.SelectValues import DefaultUseCases
from utils.utils import JSON_SELECTED_USE_CASE_PATH
import json
import streamlit.components.v1 as components

run_redirect(Page.WELCOME.value)

st.header("Welcome to the METIS-Demonstrator – Your Smart Guide for Collaborative IT Tool Stacks")

st.write("We’re glad you’re here!")
st.write("WThis website is the interactive demonstrator of a recommendation system developed as part of the <b>METIS Research Project founded by BMBF Germany.</b>", unsafe_allow_html=True)
st.write("Our goal: helping you identify the most suitable IT tools for <b>collaboration in engineering</b> – tailored to your specific needs.", unsafe_allow_html=True)
st.subheader("Why Collaboration Matters?")
st.write(
    """
    <p>
      Collaboration is the highest form of working together. It goes beyond simple coordination or cooperation, requiring a shared commitment to achieve a common goal that no partner could reach alone.
    </p>
    <p>
      In engineering, this means:
    </p>
    <ul>
      <li><b>Integrating diverse expertise</b> across different disciplines.</li>
      <li><b>Connecting workflows and processes</b> into a seamless whole.</li>
      <li><b>Leveraging the right tools</b> to enable transparency, efficiency, and innovation.</li>
    </ul>
    <p>
      The right IT tool stack is not just a collection of applications – it is the backbone of effective collaboration. It ensures that information flows smoothly, decisions are made quickly, and all contributors remain aligned, no matter where they are or what systems they use.
    </p>
    """,
    unsafe_allow_html=True
)

st.write("---")
st.subheader("How to Use the Demonstrator")
st.write("""
<b>1. By Activity Selection:</b> 
         <p>Pick the used engineering activities you perform, and we’ll suggest an optimized tool stack to support them.</p>
         """, unsafe_allow_html=True)


if st.button("🛠️ Proceed to Tool Stack and Manual Tasks Entry"):
  save_current_page(Page.TOOLS)
  st.switch_page(Page.TOOLS.value)

st.write("""
<b>2. By Use Case Select:</b> <p>Select a specific engineering use case and receive a general recommended IT tool stack without detailed input data.</p>
         """, unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
  default_use_case = st.selectbox("Select your Use Case", DefaultUseCases)

if st.button("💾 Save Use Case and Continue to Recommendations"):
  with open(JSON_SELECTED_USE_CASE_PATH, "w") as f:
    json.dump({"selected_use_case": default_use_case}, f)
    save_current_page(Page.READY_USE_CASE)
    st.switch_page(Page.READY_USE_CASE.value)

st.write("---")
st.subheader("The METIS Project")
st.write("This demonstrator is a result of the METIS Research Project, which explores how modern IT systems can enhance collaboration in complex engineering environments. By analyzing workflows, tool integrations, and team needs, we aim to bridge the gap between technical possibilities and real-world collaboration success.")
st.write("Start exploring and find your perfect collaborative IT tool setup – optimized for your work, your team, and your goals.")


col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
col1.image("assets/logo1.png", use_container_width=True)
col2.image("assets/logo2.png", use_container_width=True)
col3.image("assets/logo3.jpg", use_container_width=True)
col4.image("assets/logo4.png", use_container_width=True)
components.html("""
<script>
                var intervalId = setInterval(function() {
                var container = window.top.document.getElementsByClassName('stHorizontalBlock')[1];
                if (container) {
                    container.style.alignItems = 'center';
                    clearInterval(intervalId);
                }
                }, 100);
                
                </script>
""")