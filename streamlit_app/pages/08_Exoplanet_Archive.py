"""
ExoX - Mod8: Exoplanet Archive Check (Placeholder)
"""

import streamlit as st

st.set_page_config(page_title="Exoplanet Archive - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

st.title("Exoplanet Archive Check")
st.info("Checking NASA Exoplanet Archive for known planets. Coming soon.")

if "additional_results" in st.session_state:
    st.write(f"Stars to check: {len(st.session_state.additional_results)}")
else:
    st.warning("No results from Additional Catalogs. Run that first.")

st.page_link("pages/07_Additional_Catalogs.py", label="Back to Additional Catalogs")
