"""
ExoX - Mod11: Habitability Grading (Stage 3)
"""

import streamlit as st

st.set_page_config(page_title="Habitability - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

st.title("Habitability Grading")
st.subheader("Stage 3: Habitability Grading")
st.info("ESI, HZD, HZ Grade, and 7-parameter analysis. Coming soon.")

if "planet_candidates" in st.session_state:
    st.write(f"Planet candidates to grade: {len(st.session_state.planet_candidates)}")
else:
    st.warning("No planet candidates. Run Transit Detection first.")

st.page_link("pages/10_Transit_Detection.py", label="Back to Transit Detection")
