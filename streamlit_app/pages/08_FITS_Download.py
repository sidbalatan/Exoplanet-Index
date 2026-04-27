"""
ExoX - Mod8: FITS Image Download (Stage 2: Exoplanet Probe)
Downloads TESS cutout FITS images for visual confirmation
"""

import streamlit as st

st.set_page_config(page_title="FITS Download - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

st.title("FITS Image Download")
st.subheader("Stage 2: Exoplanet Probe — Visual Confirmation")
st.info("This module will download TESS FITS images for your certified K-dwarfs. Coming soon.")

if "certified_k_dwarfs" in st.session_state:
    st.success(f"{len(st.session_state.certified_k_dwarfs)} certified K-dwarfs ready for Stage 2")
else:
    st.warning("No certified K-dwarfs. Complete Stage 1 first.")

st.page_link("pages/07_Additional_Catalogs.py", label="Back to Stage 1")
