"""
ExoX - Mod9: Light Curve Generation (Stage 2: Exoplanet Probe)
"""

import streamlit as st

st.set_page_config(page_title="Light Curves - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

st.title("Light Curve Generation")
st.subheader("Stage 2: Exoplanet Probe")
st.info("This module will generate real TESS light curves. Coming soon.")

if "fits_results" in st.session_state:
    st.write(f"Stars ready for light curves: {len(st.session_state.fits_results)}")
else:
    st.warning("No FITS images. Run FITS Download first.")

st.page_link("pages/08_FITS_Download.py", label="Back to FITS Download")
