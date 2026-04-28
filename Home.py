"""
ExoX - Exoplanet Index
K-Dwarf Exoplanet Search Pipeline
Landing Page (Mod0)
"""

import streamlit as st

st.set_page_config(
    page_title="ExoX - Exoplanet Index",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("ExoX")
st.subheader("Exoplanet Index for K-Dwarf Stars")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="K-Dwarfs in Database", value="1,135")
with col2:
    st.metric(label="Pipeline Modules", value="15")
with col3:
    st.metric(label="Catalogs Used", value="8")
with col4:
    st.metric(label="Export Formats", value="3")

st.markdown("---")

st.markdown("## Quick Demo: Experience the Full Pipeline")
st.markdown("""
Want to see the complete pipeline in action? Click below to run a simulated demo 
with dummy data through all four stages. No login required.
""")

col_demo1, col_demo2, col_demo3 = st.columns([1, 1, 1])
with col_demo2:
    if st.button("Run Simulated Demo", type="primary", use_container_width=True):
        st.switch_page("pages/00_Simulated_Demo.py")

st.markdown("---")
st.header("What is ExoX?")

st.markdown("""
ExoX is a mobile-friendly web application designed for the astronomy community.
It helps researchers search for K-dwarf stars, filter candidates, generate 
TESS light curves, grade habitability, and share discoveries.
""")

st.markdown("---")
st.header("How It Works")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown("#### 1. Register")
with col2:
    st.markdown("#### 2. Input")
with col3:
    st.markdown("#### 3. Filter")
with col4:
    st.markdown("#### 4. Analyze")
with col5:
    st.markdown("#### 5. Share")

st.markdown("---")

col_left, col_right = st.columns(2)
with col_left:
    st.markdown("### Ready to Start?")
    if st.button("Register", type="primary", use_container_width=True):
        st.switch_page("pages/01_Register.py")
with col_right:
    st.markdown("### Already Have an Account?")
    if st.button("Login", use_container_width=True):
        st.switch_page("pages/01_Register.py")

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>"
    "ExoX v0.1 | Built for the Astronomy Community | "
    "<a href='https://github.com/sidbalatan/Exoplanet-Index'>GitHub</a>"
    "</p>",
    unsafe_allow_html=True
)
