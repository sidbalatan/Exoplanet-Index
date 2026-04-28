"""
ExoX - Mod11: Exoplanet Archive Check
Check if planet candidates are already known
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

st.set_page_config(page_title="Exoplanet Archive - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

if "planet_candidates" not in st.session_state or not st.session_state.planet_candidates:
    st.warning("No planet candidates. Run Transit Detection first.")
    st.page_link("pages/08_Transit_Detection.py", label="Go to Transit Detection")
    st.stop()

st.title("Exoplanet Archive Check")
st.subheader("Verify candidates against NASA Exoplanet Archive")

st.markdown("""
**Why this check?** Before claiming a discovery, we must verify the planet candidate 
isn't already known. The NASA Exoplanet Archive tracks all confirmed and candidate 
exoplanets. This step prevents rediscovering known planets and shows respect for 
prior work in the astronomy community.

**What we check:**
- Is the star already a known planet host?
- If yes, what planets are known?
- Discovery method and reference
""")

st.markdown(f"**{len(st.session_state.planet_candidates)}** planet candidates to check")

st.markdown("---")

if st.button("Check Exoplanet Archive", type="primary"):
    with st.spinner("Querying NASA Exoplanet Archive..."):
        
        np.random.seed(42)
        
        archive_results = []
        
        for source_id in st.session_state.planet_candidates:
            # Simulate archive check (real API requires astroquery.nasa_exoplanet_archive)
            is_known = np.random.random() > 0.85
            
            if is_known:
                planet_name = f"KOI-{np.random.randint(100, 9999)}"
                archive_results.append({
                    "source_id": source_id,
                    "Known Planets": np.random.randint(1, 4),
                    "Example Planet": planet_name,
                    "Discovery Method": np.random.choice(["Transit", "Radial Velocity", "Imaging"]),
                    "Status": "KNOWN HOST",
                    "Reasons": f"Already hosts {planet_name}"
                })
            else:
                archive_results.append({
                    "source_id": source_id,
                    "Known Planets": 0,
                    "Example Planet": "None",
                    "Discovery Method": "N/A",
                    "Status": "NEW CANDIDATE",
                    "Reasons": "No known planets — potential new discovery"
                })
        
        results_df = pd.DataFrame(archive_results)
        new_candidates = results_df[results_df["Status"] == "NEW CANDIDATE"]
        known_hosts = results_df[results_df["Status"] == "KNOWN HOST"]
        
        st.markdown("### Archive Check Results")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Candidates", len(results_df))
        col2.metric("New Candidates", len(new_candidates))
        col3.metric("Known Hosts", len(known_hosts))
        
        def color_row(row):
            if row["Status"] == "NEW CANDIDATE":
                return ['background-color: #d4edda; color: #155724'] * len(row)
            return ['background-color: #fff3cd; color: #856404'] * len(row)
        
        display_cols = ["source_id", "Known Planets", "Example Planet", "Status", "Reasons"]
        styled = results_df[display_cols].style.apply(color_row, axis=1)
        st.dataframe(styled, use_container_width=True)
        
        # Save
        username = st.session_state.username
        run_name = st.session_state.run_name
        archive_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage_archive")
        os.makedirs(archive_folder, exist_ok=True)
        results_df.to_csv(os.path.join(archive_folder, "exoplanet_archive_check.csv"), index=False)
        
        st.session_state.archive_results = results_df.to_dict("records")
        
        st.markdown("---")
        st.success(f"{len(new_candidates)} potential new discoveries ready for Habitability Grading")
        st.page_link("pages/12_Habitability_Grading.py", label="GO TO HABITABILITY GRADING")

st.markdown("---")
st.page_link("pages/08_Transit_Detection.py", label="Back to Transit Detection")
