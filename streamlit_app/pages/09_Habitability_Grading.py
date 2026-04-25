"""
ExoX - Mod9: Habitability Grading (Placeholder)
"""

import streamlit as st

st.set_page_config(page_title="Habitability - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

st.title("Habitability Grading")
st.info("ESI, HZD, HZ Grade A+ to F. Coming soon.")

if "archive_results" in st.session_state:
    st.write(f"Stars to grade: {len(st.session_state.archive_results)}")
else:
    st.warning("No results from Exoplanet Archive. Run that first.")

st.page_link("pages/08_Exoplanet_Archive.py", label="Back to Exoplanet Archive")
