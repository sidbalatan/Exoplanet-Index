"""
ExoX - Mod6: 2MASS Cross-Match
Real 2MASS queries for near-IR color confirmation
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

st.set_page_config(page_title="2MASS Match - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

if "simbad_results" not in st.session_state or not st.session_state.simbad_results:
    st.warning("No SIMBAD results. Run SIMBAD first.")
    st.page_link("pages/05_SIMBAD_CrossMatch.py", label="Go to SIMBAD")
    st.stop()

simbad_df = pd.DataFrame(st.session_state.simbad_results)
passed_simbad = simbad_df[simbad_df["_passed"] == True].copy()

if len(passed_simbad) == 0:
    st.warning("No stars passed SIMBAD.")
    st.stop()

st.title("2MASS Cross-Match")
st.subheader("Confirm K-dwarf nature with near-infrared colors")

st.markdown("""
Queries **2MASS** for J, H, Ks magnitudes. K-dwarfs have distinct J-Ks colors 
between 0.5 and 0.9, separating them from M-dwarfs and G stars.
""")

st.markdown(f"**{len(passed_simbad)}** stars to verify")

st.markdown("---")

if st.button("Run 2MASS Cross-Match", type="primary"):
    with st.spinner("Querying 2MASS..."):
        
        twomass_results = []
        
        for _, star in passed_simbad.iterrows():
            source_id = star.get("source_id", "unknown")
            ra = star.get("_ra")
            dec = star.get("_dec")
            
            if ra is None or dec is None:
                continue

            try:
                from astroquery.ipac.irsa import Irsa
                
                result = Irsa.query_region(f"{ra} {dec}", catalog="fp_psc", radius="0:0:2")
                
                if result is not None and len(result) > 0:
                    row = result[0]
                    j_mag = row.get("j_m")
                    h_mag = row.get("h_m")
                    k_mag = row.get("k_m")
                    
                    if j_mag and k_mag:
                        jk = float(j_mag) - float(k_mag)
                        passes_jk = 0.5 <= jk <= 0.9
                        
                        twomass_results.append({
                            "source_id": str(source_id),
                            "J mag": str(j_mag),
                            "H mag": str(h_mag) if h_mag else "N/A",
                            "Ks mag": str(k_mag),
                            "J-Ks (0.50-0.90)": round(jk, 2),
                            "Status": "PASSED" if passes_jk else "FAILED",
                            "Reasons": f"J-Ks={jk:.2f}" if not passes_jk else "K-dwarf color confirmed",
                            "_passed": passes_jk,
                            "_ra": ra,
                            "_dec": dec
                        })
                    else:
                        twomass_results.append({
                            "source_id": str(source_id),
                            "J-Ks (0.50-0.90)": "N/A",
                            "Status": "INCOMPLETE",
                            "Reasons": "Missing photometry",
                            "_passed": False
                        })
                else:
                    twomass_results.append({
                        "source_id": str(source_id),
                        "J-Ks (0.50-0.90)": "N/A",
                        "Status": "NOT FOUND",
                        "Reasons": "Not in 2MASS",
                        "_passed": False
                    })

            except Exception as e:
                twomass_results.append({
                    "source_id": str(source_id),
                    "J-Ks (0.50-0.90)": "ERROR",
                    "Status": "ERROR",
                    "Reasons": str(e)[:80],
                    "_passed": False
                })

        if twomass_results:
            results_df = pd.DataFrame(twomass_results)
            passed = results_df[results_df["_passed"] == True]
            
            st.markdown("### 2MASS Results")
            col1, col2, col3 = st.columns(3)
            col1.metric("Queried", len(results_df))
            col2.metric("Passed", len(passed))
            col3.metric("Failed", len(results_df) - len(passed))
            
            def color_row(row):
                if row["Status"] == "PASSED":
                    return ['background-color: #d4edda; color: #155724'] * len(row)
                return ['background-color: #f8d7da; color: #721c24'] * len(row)
            
            display_cols = ["source_id", "J mag", "Ks mag", "J-Ks (0.50-0.90)", "Status", "Reasons"]
            styled = results_df[display_cols].style.apply(color_row, axis=1)
            st.dataframe(styled, use_container_width=True)
            
            # Save
            username = st.session_state.username
            run_name = st.session_state.run_name
            run_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage4_2mass")
            os.makedirs(run_folder, exist_ok=True)
            results_df.to_csv(os.path.join(run_folder, "twomass_appended.csv"), index=False)
            
            st.session_state.twomass_results = results_df.to_dict("records")
            st.session_state.n_twomass_passed = len(passed)
            
            if len(passed) > 0:
                st.markdown("---")
                st.page_link("pages/10_WISE_AllWISE.py", label="GO TO ADDITIONAL CATALOGS")

st.markdown("---")
st.page_link("pages/05_SIMBAD_CrossMatch.py", label="Back to SIMBAD")
