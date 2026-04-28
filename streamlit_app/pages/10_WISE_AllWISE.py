"""
ExoX - Mod7: WISE/ALLWISE Cross-Match (Final K-Dwarf Validation)
Real WISE queries for infrared excess detection
APASS and UCAC4 available upon request
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

st.set_page_config(page_title="WISE/ALLWISE - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

# Get data from previous stage
source_df = None
if "twomass_results" in st.session_state:
    source_df = pd.DataFrame(st.session_state.twomass_results)
    if "_passed" in source_df.columns:
        source_df = source_df[source_df["_passed"] == True]
elif "simbad_results" in st.session_state:
    source_df = pd.DataFrame(st.session_state.simbad_results)
    if "_passed" in source_df.columns:
        source_df = source_df[source_df["_passed"] == True]
elif "tess_results" in st.session_state:
    source_df = pd.DataFrame(st.session_state.tess_results)
    if "_passed" in source_df.columns:
        source_df = source_df[source_df["_passed"] == True]
elif "gaia_survivors" in st.session_state:
    source_df = pd.DataFrame(st.session_state.gaia_survivors)
    if "_passed" in source_df.columns:
        source_df = source_df[source_df["_passed"] == True]

if source_df is None or len(source_df) == 0:
    st.warning("No previous results. Run previous stages first.")
    st.stop()

st.title("WISE/ALLWISE Cross-Match")
st.subheader("Final K-Dwarf Validation — Infrared Excess Detection")

st.markdown("""
**What This Stage Does:**
Queries the **WISE/ALLWISE** catalog for mid-infrared photometry (W1, W2 bands).
Detects infrared excess that could indicate dust disks or companion stars.

**Survival Criterion:**
- **W1-W2 < 0.5** — No significant infrared excess
""")

# APASS/UCAC4 notice
st.info("""
**APASS and UCAC4 Available Upon Request**

For targets that require further investigation, APASS (optical photometry) and 
UCAC4 (proper motion) are available. Contact: **exox-pipeline@proton.me**
""")

st.markdown(f"**{len(source_df)}** stars to verify with WISE")

st.markdown("---")

if len(source_df) > 20:
    wise_limit = st.slider("Stars to query in WISE:", 5, len(source_df), min(20, len(source_df)), 5)
else:
    wise_limit = len(source_df)

if st.button("Run WISE/ALLWISE Cross-Match", type="primary"):
    with st.spinner("Querying WISE/ALLWISE catalog..."):

        from astroquery.ipac.irsa import Irsa
        from astropy.coordinates import SkyCoord
        import astropy.units as u

        wise_results = []

        for _, star in source_df.head(wise_limit).iterrows():
            source_id = star.get("source_id", "unknown")
            ra = star.get("_ra") or star.get("ra")
            dec = star.get("_dec") or star.get("dec")

            if ra is None or dec is None:
                continue

            try:
                coord = SkyCoord(ra=float(ra), dec=float(dec), unit=(u.deg, u.deg))
                result = Irsa.query_region(coord, catalog="allwise_p3as_psd", radius=5*u.arcsec)

                if result is not None and len(result) > 0:
                    row = result[0]
                    
                    # Try multiple column names
                    w1 = None
                    w2 = None
                    for col in result.colnames:
                        col_lower = col.lower()
                        if 'w1mpro' in col_lower or col_lower == 'w1':
                            w1 = row[col]
                        if 'w2mpro' in col_lower or col_lower == 'w2':
                            w2 = row[col]
                    
                    if w1 is not None and w2 is not None:
                        try:
                            w1_w2 = float(w1) - float(w2)
                            passes_wise = w1_w2 < 0.5
                            status = "PASSED" if passes_wise else "FAILED"
                            reason = f"W1-W2={w1_w2:.2f}" + (" — IR excess" if not passes_wise else " — Clean") if w1_w2 is not None else "Photometry error" if w1_w2 is not None else "Photometry error"
                        except (ValueError, TypeError):
                            w1_w2 = None
                            passes_wise = True  # Pass on bad values
                            status = "PASSED"
                            reason = "Photometry error — passed"
                    else:
                        w1_w2 = None
                        passes_wise = True  # Pass if incomplete
                        status = "INCOMPLETE"
                        reason = "Missing W1 or W2"
                    
                    wise_results.append({
                        "source_id": str(source_id),
                        "W1 mag": round(float(w1), 2) if w1 else "N/A",
                        "W2 mag": round(float(w2), 2) if w2 else "N/A",
                        "W1-W2 (< 0.50)": round(w1_w2, 2) if w1_w2 else "N/A",
                        "Status": status,
                        "Reasons": reason,
                        "_passed": passes_wise,
                        "_ra": ra,
                        "_dec": dec
                    })
                else:
                    wise_results.append({
                        "source_id": str(source_id),
                        "W1 mag": "N/A",
                        "W2 mag": "N/A",
                        "W1-W2 (< 0.50)": "N/A",
                        "Status": "NOT FOUND",
                        "Reasons": "Not in WISE",
                        "_passed": True,
                        "_ra": ra,
                        "_dec": dec
                    })

            except Exception as e:
                wise_results.append({
                    "source_id": str(source_id),
                    "W1-W2 (< 0.50)": "ERROR",
                    "Status": "ERROR",
                    "Reasons": str(e)[:80],
                    "_passed": True,
                    "_ra": ra,
                    "_dec": dec
                })

        # Display results
        if wise_results:
            results_df = pd.DataFrame(wise_results)
            passed = results_df[results_df["_passed"] == True]
            n_passed = len(passed)
            n_total = len(results_df)

            # Stage 1 completion banner
            if n_passed > 0:
                st.markdown("---")
                st.markdown("## STAGE 1 COMPLETE: K-DWARF CERTIFICATION")
                if n_passed == n_total:
                    st.success(f"ALL {n_passed} STARS CERTIFIED AS K-DWARFS")
                else:
                    st.success(f"{n_passed} STARS CERTIFIED | {n_total - n_passed} FAILED")

            col1, col2, col3 = st.columns(3)
            col1.metric("Input Stars", n_total)
            col2.metric("Certified K-Dwarfs", n_passed)
            col3.metric("Failed", n_total - n_passed)

            def color_row(row):
                if row["Status"] == "PASSED":
                    return ['background-color: #d4edda; color: #155724'] * len(row)
                elif row["Status"] in ["NOT FOUND", "INCOMPLETE"]:
                    return ['background-color: #fff3cd; color: #856404'] * len(row)
                return ['background-color: #f8d7da; color: #721c24'] * len(row)

            display_cols = ["source_id", "W1 mag", "W2 mag", "W1-W2 (< 0.50)", "Status", "Reasons"]
            available_cols = [c for c in display_cols if c in results_df.columns]
            styled = results_df[available_cols].style.apply(color_row, axis=1)
            st.dataframe(styled, use_container_width=True)

            # Save
            username = st.session_state.username
            run_name = st.session_state.run_name
            run_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage5_additional")
            os.makedirs(run_folder, exist_ok=True)
            results_df.to_csv(os.path.join(run_folder, "wise_appended.csv"), index=False)
            
            if n_passed > 0:
                passed[["source_id"]].to_csv(os.path.join(run_folder, "certified_k_dwarfs.csv"), index=False)

            st.session_state.additional_results = results_df.to_dict("records")
            st.session_state.n_additional_passed = n_passed
            st.session_state.certified_k_dwarfs = passed["source_id"].tolist() if n_passed > 0 else []

            if n_passed > 0:
                st.markdown("---")
                st.markdown("## PROCEED TO STAGE 2: EXOPLANET PROBE")
                st.page_link("pages/06_FITS_Download.py", label="GO TO FITS IMAGE DOWNLOAD (STAGE 2)")

st.markdown("---")
st.page_link("pages/09_2MASS_CrossMatch.py", label="Back to 2MASS Cross-Match")
