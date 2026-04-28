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

# Stats row
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

# Quick Demo Section
st.markdown("## Quick Demo: Experience the Full Pipeline")
st.markdown("""
Want to see the complete pipeline in action? Click below to run a **simulated demo** 
with dummy data. You'll see all four stages:
1. **K-Dwarf Search** — Validating a star across 5 catalogs
2. **Exoplanet Probe** — FITS images, light curves, and transit detection
3. **Habitability Grading** — 7-parameter analysis with letter grades
4. **Community Sharing** — Share your discoveries

No login required for the demo. Results are simulated for demonstration purposes.
""")

col_demo1, col_demo2, col_demo3 = st.columns([1, 1, 1])
with col_demo2:
    if st.button("Run Simulated Demo", type="primary", use_container_width=True):
        st.switch_page("pages/00_Simulated_Demo.py")

st.markdown("---")
st.header("What is ExoX?")

st.markdown("""
ExoX is a **mobile-friendly web application** designed for the astronomy community.
It helps researchers:

- **Search** for K-dwarf stars using Gaia DR3, TESS, SIMBAD, 2MASS, and other catalogs
- **Filter** candidates using scientifically validated criteria
- **Generate** TESS light curves for transit detection
- **Grade** habitability using ESI, HZD, and letter grades (A+ to F)
- **Export** results in CSV, VOTable, and FITS formats
- **Share** discoveries with the community through the gallery
""")

st.markdown("---")
st.header("How It Works")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown("#### 1. Register")
    st.markdown("Create an account with email verification.")
with col2:
    st.markdown("#### 2. Input")
    st.markdown("Enter Gaia DR3 IDs or upload a CSV.")
with col3:
    st.markdown("#### 3. Filter")
    st.markdown("Run the 8-stage K-dwarf pipeline.")
with col4:
    st.markdown("#### 4. Analyze")
    st.markdown("Generate TESS light curves for candidates.")
with col5:
    st.markdown("#### 5. Share")
    st.markdown("Upload results to the community gallery.")

st.markdown("---")

col_left, col_right = st.columns(2)
with col_left:
    st.markdown("### Ready to Start?")
    st.markdown("Register an account to begin searching for exoplanets.")
    if st.button("Register", type="primary", use_container_width=True):
        st.switch_page("pages/01_Register.py")
with col_right:
    st.markdown("### Already Have an Account?")
    st.markdown("Login to access your dashboard and previous runs.")
    if st.button("Login", use_container_width=True):
        st.switch_page("pages/01_Register.py")

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>"
    "ExoX v0.1 | Built for the Astronomy Community | "
    "<a href='https://github.com/sidbalatan/Exoplanet-Index' target='_blank'>GitHub</a>"
    "</p>",
    unsafe_allow_html=True
)
