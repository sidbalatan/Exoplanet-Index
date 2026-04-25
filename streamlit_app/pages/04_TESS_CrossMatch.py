"""
ExoX - Mod4: TESS Cross-Match (Placeholder)
"""

import streamlit as st

st.set_page_config(page_title="TESS Match - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

st.title("TESS Cross-Match")
st.info("This module will cross-match survivors with the TESS Input Catalog. Coming soon.")

if "gaia_survivors" in st.session_state:
    st.write(f"Gaia survivors to match: {len(st.session_state.gaia_survivors)}")
else:
    st.warning("No Gaia survivors. Run Gaia Filter first.")

st.page_link("pages/03_Gaia_Filter.py", label="Back to Gaia Filter")
st.page_link("Home.py", label="Back to Home")
