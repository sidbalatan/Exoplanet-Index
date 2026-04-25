"""
ExoX - Exoplanet Index
K-Dwarf Exoplanet Search Pipeline
Landing Page (Mod0)
"""

import streamlit as st

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="ExoX - Exoplanet Index",
    page_icon=":telescope:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# HEADER
# ============================================
st.title("ExoX")
st.subheader("Exoplanet Index for K-Dwarf Stars")

# ============================================
# STATS ROW
# ============================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="K-Dwarfs in Database", value="1,135")
with col2:
    st.metric(label="Pipeline Modules", value="16")
with col3:
    st.metric(label="Catalogs Used", value="8")
with col4:
    st.metric(label="Export Formats", value="3")

# ============================================
# WHAT IS EXOX
# ============================================
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

# ============================================
# HOW IT WORKS
# ============================================
st.markdown("---")
st.header("How It Works")

step_col1, step_col2, step_col3, step_col4, step_col5 = st.columns(5)

with step_col1:
    st.markdown("#### 1. Register")
    st.markdown("Create an account with email verification.")

with step_col2:
    st.markdown("#### 2. Input")
    st.markdown("Enter Gaia DR3 IDs or upload a CSV.")

with step_col3:
    st.markdown("#### 3. Filter")
    st.markdown("Run the 8-stage K-dwarf pipeline.")

with step_col4:
    st.markdown("#### 4. Analyze")
    st.markdown("Generate TESS light curves for candidates.")

with step_col5:
    st.markdown("#### 5. Share")
    st.markdown("Upload results to the community gallery.")

# ============================================
# PIPELINE STAGES OVERVIEW
# ============================================
st.markdown("---")
st.header("Pipeline Stages")

st.markdown("""
| Stage | Module | What It Does |
|-------|--------|-------------|
| 1 | Gaia DR3 Filter | Queries Gaia archive, applies K-dwarf cuts (Teff, logg, parallax, RUWE) |
| 2 | TESS Cross-Match | Adds TIC parameters and observation info |
| 3 | SIMBAD Cross-Match | Verifies spectral type, flags binaries and variables |
| 4 | 2MASS Cross-Match | Adds near-IR photometry, confirms K-dwarf colors |
| 5 | Additional Catalogs | WISE, APASS, UCAC4 for multi-wavelength confirmation |
| 6 | Exoplanet Archive | Checks for known planets, prevents rediscovery |
| 7 | Habitability Grading | ESI, HZD, HZ Grade A+ to F |
| 8 | Final Report | Merges all data, generates plots and exports |
""")

# ============================================
# CALL TO ACTION
# ============================================
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

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>"
    "ExoX v0.1 | Built for the Astronomy Community | "
    "<a href='https://github.com/sidbalatan/Exoplanet-Index' target='_blank'>GitHub</a>"
    "</p>",
    unsafe_allow_html=True
)