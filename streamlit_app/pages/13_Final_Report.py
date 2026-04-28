"""
ExoX - Mod13: Final Report (Stage 4: Community Sharing)
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Final Report - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

st.title("Final Report")
st.subheader("Stage 4: Community Sharing")

st.success("Pipeline Complete! Your results are ready for export and sharing.")

# Export buttons
if "habitability_results" in st.session_state:
    habit_df = pd.DataFrame(st.session_state.habitability_results)
    
    st.markdown("### Your Results")
    st.dataframe(habit_df, use_container_width=True)
    
    csv = habit_df.to_csv(index=False)
    st.download_button("DOWNLOAD CSV", csv, f"exox_results_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    
    st.markdown("---")
    st.markdown("### Share Your Discovery")
    st.page_link("pages/14_User_Gallery.py", label="UPLOAD TO GALLERY")
else:
    st.info("Complete the full pipeline to see your final report.")

st.markdown("---")
st.page_link("Home.py", label="BACK TO HOME")
