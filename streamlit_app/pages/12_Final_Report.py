"""
ExoX - Mod12: Final Report (Stage 4: Community Sharing)
"""

import streamlit as st

st.set_page_config(page_title="Final Report - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

st.title("Final Report")
st.subheader("Stage 4: Community Sharing")
st.info("Final catalog merge, plots, and export. Coming soon.")

if "habitability_results" in st.session_state:
    st.write(f"Stars in final catalog: {len(st.session_state.habitability_results)}")
else:
    st.warning("No habitability results. Run Habitability Grading first.")

st.page_link("pages/11_Habitability_Grading.py", label="Back to Habitability Grading")
