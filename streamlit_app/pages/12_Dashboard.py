"""
ExoX - Mod12: User Dashboard (Placeholder)
"""

import streamlit as st

st.set_page_config(page_title="Dashboard - ExoX", page_icon=":bar_chart:", layout="wide")

st.title("Dashboard")
st.info("Dashboard module coming soon.")

if st.button("Back to Home"):
    st.switch_page("Home.py")
