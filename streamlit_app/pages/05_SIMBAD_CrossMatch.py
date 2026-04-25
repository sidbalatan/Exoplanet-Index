"""
ExoX - Mod5: SIMBAD Cross-Match (Placeholder)
"""

import streamlit as st

st.set_page_config(page_title="SIMBAD Match - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

st.title("SIMBAD Cross-Match")
st.info("This module will cross-match with SIMBAD. Coming soon.")

if "tess_results" in st.session_state:
    st.write(f"TESS-matched stars to verify: {len(st.session_state.tess_results)}")
else:
    st.warning("No TESS results. Run TESS Cross-Match first.")

st.page_link("pages/04_TESS_CrossMatch.py", label="Back to TESS Cross-Match")
