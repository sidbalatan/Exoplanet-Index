"""
ExoX - Mod10: Transit Detection (Stage 2: Exoplanet Probe)
"""

import streamlit as st

st.set_page_config(page_title="Transit Detection - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

st.title("Transit Detection")
st.subheader("Stage 2: Exoplanet Probe")
st.info("This module will run BLS periodogram and phase-folding. Coming soon.")

if "lightcurve_results" in st.session_state:
    st.write(f"Stars to analyze: {len(st.session_state.lightcurve_results)}")
else:
    st.warning("No light curves. Generate light curves first.")

st.page_link("pages/09_LightCurve_Generation.py", label="Back to Light Curves")
