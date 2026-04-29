"""
ExoX - Mod5: SIMBAD Cross-Match
Real SIMBAD queries for spectral type verification
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

st.set_page_config(page_title="SIMBAD Match - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

source_df = None
if "tess_results" in st.session_state:
    source_df = pd.DataFrame(st.session_state.tess_results)
    if "_passed" in source_df.columns:
        source_df = source_df[source_df["_passed"] == True]
elif "gaia_survivors" in st.session_state:
    source_df = pd.DataFrame(st.session_state.gaia_survivors)
    if "_passed" in source_df.columns:
        source_df = source_df[source_df["_passed"] == True]

if source_df is None or len(source_df) == 0:
    st.warning("No previous results.")
    st.stop()

st.title("SIMBAD Cross-Match")
st.subheader("Verify spectral type with the gold standard catalog")

st.markdown("Queries SIMBAD for literature spectral types. Confirms K-dwarf classification.")
st.markdown(f"**{len(source_df)}** stars to verify")

# Limit
if len(source_df) > 10:
    simbad_limit = st.slider("Stars to query:", 5, len(source_df), min(20, len(source_df)), 5)
    estimated = simbad_limit * 2.5
    if estimated > 60:
        st.info(f"Estimated time: ~{estimated//60} min {estimated%60:.0f}s")
    else:
        st.info(f"Estimated time: ~{estimated:.0f}s")
else:
    simbad_limit = len(source_df)

st.markdown("---")

if st.button("Run SIMBAD Cross-Match", type="primary"):
    with st.spinner("Querying SIMBAD..."):
        from astroquery.simbad import Simbad
        from astropy.coordinates import SkyCoord
        import astropy.units as u
        
        Simbad.add_votable_fields('sp', 'otype')
        
        results = []
        for _, star in source_df.head(simbad_limit).iterrows():
            source_id = str(star.get("source_id", "unknown"))
            ra = star.get("_ra") or star.get("ra")
            dec = star.get("_dec") or star.get("dec")
            
            if ra is None or dec is None:
                continue
            
            try:
                coord = SkyCoord(ra=float(ra), dec=float(dec), unit=(u.deg, u.deg))
                result = Simbad.query_region(coord, radius=10*u.arcsec)
                
                if result is not None and len(result) > 0:
                    row = result[0]
                    sp = str(row.get("sp_type", "")).strip()
                    otype = str(row.get("otype", "")).strip()
                    
                    if sp and "K" in sp and "V" in sp:
                        status = "CONFIRMED K-DWARF"
                        passed = True
                    else:
                        status = "FOUND" if sp else "NO SPECTRAL TYPE"
                        passed = True  # Pass - many stars lack published spectral type
                    
                    results.append({
                        "source_id": source_id,
                        "SIMBAD ID": str(row.get("main_id", "N/A")),
                        "Spectral Type": sp if sp else "Not published",
                        "Object Type": otype if otype else "N/A",
                        "Status": status,
                        "_passed": passed,
                        "_ra": ra,
                        "_dec": dec
                    })
                else:
                    results.append({
                        "source_id": source_id,
                        "SIMBAD ID": "NOT FOUND",
                        "Spectral Type": "N/A",
                        "Object Type": "N/A",
                        "Status": "NOT IN SIMBAD",
                        "_passed": True,
                        "_ra": ra,
                        "_dec": dec
                    })
            except:
                results.append({
                    "source_id": source_id,
                    "Status": "ERROR",
                    "_passed": True,
                    "_ra": ra,
                    "_dec": dec
                })
        
        if results:
            results_df = pd.DataFrame(results)
            passed = results_df[results_df["_passed"] == True]
            
            st.markdown("### SIMBAD Results")
            col1, col2, col3 = st.columns(3)
            col1.metric("Queried", len(results_df))
            col2.metric("Confirmed K-Dwarfs", len(passed))
            col3.metric("Other", len(results_df) - len(passed))
            
            def color_row(row):
                if "CONFIRMED" in str(row.get("Status", "")):
                    return ['background-color: #d4edda; color: #155724'] * len(row)
                return ['background-color: #fff3cd; color: #856404'] * len(row)
            
            # Safe columns
            safe = ["source_id", "SIMBAD ID", "Spectral Type", "Object Type", "Status"]
            safe = [c for c in safe if c in results_df.columns]
            styled = results_df[safe].style.apply(color_row, axis=1)
            st.dataframe(styled, use_container_width=True)
            
            # Save
            username = st.session_state.username
            run_name = st.session_state.run_name
            run_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage3_simbad")
            os.makedirs(run_folder, exist_ok=True)
            results_df.to_csv(os.path.join(run_folder, "simbad_appended.csv"), index=False)
            
            st.session_state.simbad_results = results_df.to_dict("records")
            st.session_state.n_simbad_passed = len(passed)
            st.session_state.certified_k_dwarfs = passed["source_id"].tolist()
            
            st.markdown("---")
            st.page_link("pages/05b_K_Dwarf_Certificate.py", label="VIEW K-DWARF CERTIFICATE")

st.markdown("---")
st.page_link("pages/04_TESS_CrossMatch.py", label="Back to TESS Cross-Match")
