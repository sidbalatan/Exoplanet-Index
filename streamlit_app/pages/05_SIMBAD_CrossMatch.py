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

if "tess_results" not in st.session_state or not st.session_state.tess_results:
    st.warning("No TESS results. Run TESS Cross-Match first.")
    st.page_link("pages/04_TESS_CrossMatch.py", label="Go to TESS Cross-Match")
    st.stop()

tess_df = pd.DataFrame(st.session_state.tess_results)
passed_tess = tess_df[tess_df["_passed"] == True].copy()

if len(passed_tess) == 0:
    st.warning("No stars passed TESS checks.")
    st.stop()

st.title("SIMBAD Cross-Match")
st.subheader("Verify spectral type with the gold standard catalog")

st.markdown("""
Queries **SIMBAD** for literature spectral types, proper motions, and binarity flags.
Ensures the star is classified as a K-dwarf in peer-reviewed literature.
""")

st.markdown(f"**{len(passed_tess)}** stars to verify")

st.markdown("---")

if st.button("Run SIMBAD Cross-Match", type="primary"):
    with st.spinner("Querying SIMBAD..."):
        
        simbad_results = []
        
        for _, star in passed_tess.iterrows():
            source_id = star.get("source_id", "unknown")
            ra = star.get("_ra")
            dec = star.get("_dec")
            
            if ra is None or dec is None:
                continue

            try:
                from astroquery.simbad import Simbad
                
                # Add fields we want
                Simbad.add_votable_fields('sp', 'pm', 'rv', 'otype')
                
                result = Simbad.query_region(f"{ra} {dec}", radius="0:0:1")
                
                if result is not None and len(result) > 0:
                    row = result[0]
                    sp_type = str(row.get("SP_TYPE", "N/A"))
                    
                    # Check if K-dwarf
                    is_k = sp_type.startswith("K") and "V" in sp_type
                    
                    simbad_results.append({
                        "source_id": str(source_id),
                        "Spectral Type": sp_type,
                        "Proper Motion RA": str(row.get("PMRA", "N/A")),
                        "Proper Motion Dec": str(row.get("PMDEC", "N/A")),
                        "Status": "CONFIRMED K-DWARF" if is_k else "CHECK TYPE",
                        "Reasons": "SIMBAD confirms K-dwarf" if is_k else f"SIMBAD type: {sp_type}",
                        "_passed": is_k,
                        "_ra": ra,
                        "_dec": dec
                    })
                else:
                    simbad_results.append({
                        "source_id": str(source_id),
                        "Spectral Type": "NOT FOUND",
                        "Proper Motion RA": "N/A",
                        "Proper Motion Dec": "N/A",
                        "Status": "NOT IN SIMBAD",
                        "Reasons": "No SIMBAD entry",
                        "_passed": False
                    })

            except Exception as e:
                simbad_results.append({
                    "source_id": str(source_id),
                    "Spectral Type": "ERROR",
                    "Status": "ERROR",
                    "Reasons": str(e)[:80],
                    "_passed": False
                })

        if simbad_results:
            results_df = pd.DataFrame(simbad_results)
            passed = results_df[results_df["_passed"] == True]
            
            st.markdown("### SIMBAD Results")
            col1, col2, col3 = st.columns(3)
            col1.metric("Queried", len(results_df))
            col2.metric("K-Dwarfs Confirmed", len(passed))
            col3.metric("Other", len(results_df) - len(passed))
            
            def color_row(row):
                if row["Status"] == "CONFIRMED K-DWARF":
                    return ['background-color: #d4edda; color: #155724'] * len(row)
                return ['background-color: #f8d7da; color: #721c24'] * len(row)
            
            display_cols = ["source_id", "Spectral Type", "Proper Motion RA", "Proper Motion Dec", "Status", "Reasons"]
            styled = results_df[display_cols].style.apply(color_row, axis=1)
            st.dataframe(styled, use_container_width=True)
            
            # Save
            username = st.session_state.username
            run_name = st.session_state.run_name
            run_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage3_simbad")
            os.makedirs(run_folder, exist_ok=True)
            results_df.to_csv(os.path.join(run_folder, "simbad_appended.csv"), index=False)
            
            st.session_state.simbad_results = results_df.to_dict("records")
            st.session_state.n_simbad_passed = len(passed)
            
            if len(passed) > 0:
                st.markdown("---")
                st.page_link("pages/06_2MASS_CrossMatch.py", label="GO TO 2MASS CROSS-MATCH")

st.markdown("---")
st.page_link("pages/04_TESS_CrossMatch.py", label="Back to TESS Cross-Match")
