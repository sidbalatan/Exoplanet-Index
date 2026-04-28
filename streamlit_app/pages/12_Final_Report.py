"""
ExoX - Mod12: Final Report (Stage 4: Community Sharing)
Merge results, export catalog, share discoveries
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Final Report - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

if "habitability_results" not in st.session_state or not st.session_state.habitability_results:
    st.warning("No habitability results. Run Habitability Grading first.")
    st.page_link("pages/11_Habitability_Grading.py", label="Go to Habitability Grading")
    st.stop()

habit_df = pd.DataFrame(st.session_state.habitability_results)

st.title("Final Report")
st.subheader("Stage 4: Community Sharing")

st.markdown("""
**Congratulations on completing the ExoX pipeline!** This module merges all your 
results into a final catalog and provides export options for sharing with the astronomy community.
""")

# ============================================
# PIPELINE FUNNEL
# ============================================
st.markdown("---")
st.markdown("## Pipeline Summary: From Input to Discovery")

n_input = st.session_state.get("n_targets", 10)
n_gaia = st.session_state.get("n_survivors", n_input)
n_tess = st.session_state.get("n_tess_passed", n_gaia)
n_simbad = st.session_state.get("n_simbad_passed", n_tess)
n_twomass = st.session_state.get("n_twomass_passed", n_simbad)
n_additional = st.session_state.get("n_additional_passed", n_twomass)
n_fits = st.session_state.get("n_fits_confirmed", n_additional)
n_planet = st.session_state.get("n_planet_candidates", len(st.session_state.get("planet_candidates", [])))
n_habitable = int(habit_df["Habitable?"].value_counts().get("YES", 0))

fig, ax = plt.subplots(figsize=(10, 5))
stages = ['Input', 'Gaia', 'TESS', 'SIMBAD', '2MASS', 'Catalogs', 'FITS', 'Planets', 'Habitable']
counts = [n_input, n_gaia, n_tess, n_simbad, n_twomass, n_additional, n_fits, n_planet, n_habitable]
colors = ['#3498db', '#2980b9', '#1abc9c', '#2ecc71', '#27ae60', '#f39c12', '#e67e22', '#e74c3c', '#c0392b']

bars = ax.bar(stages, counts, color=colors, edgecolor='white', linewidth=2)
for bar, count in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, str(count),
            ha='center', va='bottom', fontweight='bold', fontsize=12)
ax.set_ylabel('Number of Stars')
ax.set_title('ExoX Pipeline Funnel')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
st.pyplot(fig)
plt.close()

# ============================================
# FINAL CATALOG
# ============================================
st.markdown("---")
st.markdown("## Final Exoplanet Catalog")

st.markdown(f"""
### Summary
- **Stars Input:** {n_input}
- **Certified K-Dwarfs:** {n_additional}
- **Planet Candidates:** {n_planet}
- **Potentially Habitable:** {n_habitable}
""")

st.dataframe(habit_df, use_container_width=True)

# Habitable highlight
if n_habitable > 0:
    st.markdown("---")
    st.success(f"POTENTIALLY HABITABLE PLANETS: {n_habitable}")
    habitable_planets = habit_df[habit_df["Habitable?"] == "YES"]
    for _, planet in habitable_planets.iterrows():
        st.markdown(f"**{planet['source_id']}** — Grade: {planet['HZ Grade']}, {planet['R_p (R_earth)']} R_earth, ESI: {planet['ESI (0-1) (> 0.8)']}")

# ============================================
# EXPORT
# ============================================
st.markdown("---")
st.markdown("## Export Your Results")

col1, col2, col3 = st.columns(3)

with col1:
    csv_data = habit_df.to_csv(index=False)
    st.download_button(
        label="DOWNLOAD CSV",
        data=csv_data,
        file_name=f"exoplanet_catalog_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    report_text = f"""EXOX FINAL REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*50}
Input: {n_input} | K-Dwarfs: {n_additional} | Planets: {n_planet} | Habitable: {n_habitable}
"""
    if n_habitable > 0:
        report_text += "\nHABITABLE PLANETS:\n"
        for _, p in habitable_planets.iterrows():
            report_text += f"{p['source_id']}: Grade {p['HZ Grade']}, {p['R_p (R_earth)']} R_earth, ESI {p['ESI (0-1) (> 0.8)']}\n"
    
    st.download_button(
        label="DOWNLOAD REPORT",
        data=report_text,
        file_name=f"exoplanet_report_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain",
        use_container_width=True
    )

with col3:
    if st.button("SAVE TO MY FOLDER", type="primary", use_container_width=True):
        username = st.session_state.username
        run_name = st.session_state.run_name
        final_folder = os.path.join("users", username, "pipeline_runs", run_name, "final_outputs")
        os.makedirs(final_folder, exist_ok=True)
        habit_df.to_csv(os.path.join(final_folder, "final_catalog.csv"), index=False)
        st.success(f"Saved to {final_folder}")

# ============================================
# SHARE
# ============================================
st.markdown("---")
st.markdown("## Share Your Discovery")

col_a, col_b = st.columns(2)
with col_a:
    st.page_link("pages/13_Editor_Gallery.py", label="GO TO EDITOR'S GALLERY")
with col_b:
    st.page_link("Home.py", label="BACK TO HOME")

st.markdown("---")
st.success("PIPELINE COMPLETE — Thank you for using ExoX!")
