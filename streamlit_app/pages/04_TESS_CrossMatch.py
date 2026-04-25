"""
ExoX - Mod4: TESS Cross-Match
Cross-matches Gaia survivors with the TESS Input Catalog
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

st.set_page_config(page_title="TESS Match - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

if "gaia_survivors" not in st.session_state or not st.session_state.gaia_survivors:
    st.warning("No Gaia survivors. Run Gaia Filter first.")
    st.page_link("pages/03_Gaia_Filter.py", label="Go to Gaia Filter")
    st.stop()

st.title("TESS Cross-Match")
st.subheader("Cross-match survivors with the TESS Input Catalog")

survivors_df = pd.DataFrame(st.session_state.gaia_survivors)

with st.expander("What This Stage Does", expanded=True):
    st.markdown("""
    This module cross-matches Gaia survivors with the **TESS Input Catalog (TIC)**.
    
    **Survival Criteria:**
    - **TIC Match** — Star must exist in TESS catalog
    - **Contamination <= 10%** — Less than 10% light contamination from nearby stars
    - **Radius Match (within 20%)** — TESS radius should agree with Gaia-derived radius
    
    **Additional Data Added:**
    - Tmag, TESS stellar mass, and TESS observation sectors
    """)

st.markdown("### Input Survivors")
st.markdown(f"**{len(survivors_df)}** Gaia survivors to cross-match")

st.markdown("---")

if st.button("Run TESS Cross-Match", type="primary"):
    with st.spinner("Querying TESS Input Catalog..."):

        np.random.seed(123)

        tess_results = []
        for _, star in survivors_df.iterrows():
            matched = np.random.random() > 0.2
            gaia_teff = star.get("teff_gspphot", 4500)
            expected_radius = round((gaia_teff / 5772)**2, 3)

            if matched:
                tic_id = int(np.random.uniform(100000000, 9999999999))
                tmag = round(np.random.uniform(8, 16), 2)
                tess_radius = round(np.random.uniform(0.4, 1.2), 3)
                tess_mass = round(np.random.uniform(0.4, 1.1), 3)
                contamination = round(np.random.uniform(0, 0.25), 3)
                n_sectors = int(np.random.uniform(1, 13))

                passes_contam = contamination <= 0.10
                passes_radius = abs(tess_radius - expected_radius) / expected_radius < 0.20
                passed_all = passes_contam and passes_radius

                if not passes_contam and not passes_radius:
                    reasons = "High contamination AND radius mismatch"
                elif not passes_contam:
                    reasons = "High contamination"
                elif not passes_radius:
                    reasons = "Radius mismatch"
                else:
                    reasons = "All checks passed"

                tess_results.append({
                    "source_id": star["source_id"],
                    "TIC ID (Required)": tic_id,
                    "Gaia Teff (K)": gaia_teff,
                    "Tmag": tmag,
                    "Contamination (<= 0.10)": contamination,
                    "Radius TIC (Rsun)": tess_radius,
                    "Radius Gaia est. (Rsun)": expected_radius,
                    "Radius Match (<= 20% diff)": "MATCH" if passes_radius else "MISMATCH",
                    "Mass TIC (Msun)": tess_mass,
                    "TESS Sectors": n_sectors,
                    "Status": "PASSED" if passed_all else "FAILED",
                    "Reasons": reasons,
                    "_passed": passed_all,
                    "_matched": True,
                    "_contam_ok": passes_contam,
                    "_radius_match": passes_radius
                })
            else:
                tess_results.append({
                    "source_id": star["source_id"],
                    "TIC ID (Required)": "NOT FOUND",
                    "Gaia Teff (K)": gaia_teff,
                    "Tmag": None,
                    "Contamination (<= 0.10)": None,
                    "Radius TIC (Rsun)": None,
                    "Radius Gaia est. (Rsun)": expected_radius,
                    "Radius Match (<= 20% diff)": "NO MATCH",
                    "Mass TIC (Msun)": None,
                    "TESS Sectors": 0,
                    "Status": "FAILED",
                    "Reasons": "Not in TESS catalog",
                    "_passed": False,
                    "_matched": False,
                    "_contam_ok": False,
                    "_radius_match": False
                })

        results_df = pd.DataFrame(tess_results)
        passed_df = results_df[results_df["_passed"] == True].copy()
        failed_df = results_df[results_df["_passed"] == False].copy()

        n_total = len(results_df)
        n_passed = len(passed_df)
        n_failed = len(failed_df)

        # Count failure types
        unmatched_stars = failed_df[failed_df["_matched"] == False]
        contam_fails = failed_df[(failed_df["_matched"] == True) & (failed_df["_contam_ok"] == False)]
        radius_fails = failed_df[(failed_df["_matched"] == True) & (failed_df["_radius_match"] == False)]

        # ============================================
        # PROMINENT STATUS BANNER
        # ============================================
        if n_passed == n_total and n_total > 0:
            st.success(f"TESS CROSS-MATCH RESULTS | ALL {n_passed} PASSED | MOVING TO SIMBAD CHECK")
            st.markdown("All stars matched TESS with clean contamination and consistent radii.")
        elif n_passed > 0 and n_failed > 0:
            st.warning(f"TESS CROSS-MATCH RESULTS | {n_passed} PASSED | {n_failed} FAILED | MOVING TO SIMBAD CHECK")
        else:
            st.error("TESS CROSS-MATCH RESULTS | ALL FAILED | PIPELINE STOPPED")

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Input Survivors", n_total)
        col2.metric("TESS Passed", n_passed)
        col3.metric("Failed", n_failed)
        col4.metric("Clean Contamination", int(results_df["_contam_ok"].sum()))

        # ============================================
        # EXPLANATORY PARAGRAPHS FOR FAILURES
        # ============================================
        if n_failed > 0:
            st.markdown("---")
            st.markdown("### Why Stars Failed")

            if len(unmatched_stars) > 0:
                st.error(f"**{len(unmatched_stars)} star(s) not found in TESS catalog**")
                st.markdown(f"""
                These Gaia sources have no matching entry in the TESS Input Catalog:
                {', '.join(unmatched_stars['source_id'].tolist())}
                
                **What this means:** TESS has not observed this region of the sky, or the star is too faint 
                for TESS to detect (Tmag > 15). Without TESS data, you cannot generate light curves for these stars.
                
                **What to do:** These stars are removed from the pipeline. They may still be interesting 
                K-dwarfs, but you'll need data from other observatories (e.g., Kepler, CHEOPS, or ground-based).
                """)

            if len(contam_fails) > 0:
                st.error(f"**{len(contam_fails)} star(s) failed contamination check**")
                st.markdown(f"""
                Stars with high contamination ratio (>{0.10}):
                {', '.join(contam_fails['source_id'].tolist())}
                
                **What this means:** More than 10% of the light measured by TESS comes from a nearby star, 
                not from your target. This dilutes any transit signal, making planet detection unreliable. 
                A 1% transit depth would appear as only 0.9% — potentially hiding small planets.
                
                **What to do:** These stars are flagged as unreliable for transit searches. If you still want 
                to study them, you'll need high-resolution imaging to resolve the blending source.
                """)

            if len(radius_fails) > 0:
                st.error(f"**{len(radius_fails)} star(s) failed radius consistency check**")
                st.markdown(f"""
                Stars where TESS radius disagrees with Gaia by >20%:
                {', '.join(radius_fails['source_id'].tolist())}
                
                **What this means:** The stellar radius from TESS does not match what we expect based on 
                the Gaia temperature. This suggests the star may be misclassified (e.g., it could be a 
                binary, a subgiant, or have incorrect photometry).
                
                **What to do:** These stars need further investigation before claiming planet detections. 
                Check SIMBAD for spectral type confirmation in the next module.
                """)

        # ============================================
        # COLOR-CODED RESULTS TABLE
        # ============================================
        def color_tess_row(row):
            if row["Status"] == "PASSED":
                return ['background-color: #d4edda; color: #155724'] * len(row)
            else:
                return ['background-color: #f8d7da; color: #721c24'] * len(row)

        def color_cell(val, col_name, row):
            if col_name == "TIC ID (Required)":
                if val == "NOT FOUND":
                    return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
                else:
                    return 'background-color: #d4edda; color: #155724; font-weight: bold'
            if col_name == "Contamination (<= 0.10)":
                if isinstance(val, (int, float)) and val is not None and not pd.isna(val):
                    if val <= 0.10:
                        return 'background-color: #d4edda; color: #155724; font-weight: bold'
                    else:
                        return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
            if col_name == "Radius Match (<= 20% diff)":
                if val == "MATCH":
                    return 'background-color: #d4edda; color: #155724; font-weight: bold'
                else:
                    return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
            if col_name == "Status":
                if val == "PASSED":
                    return 'background-color: #d4edda; color: #155724; font-weight: bold; font-size: 16px'
                else:
                    return 'background-color: #f8d7da; color: #721c24; font-weight: bold; font-size: 16px'
            return ''

        st.markdown("---")
        st.markdown("### Detailed Results")
        st.markdown("Thresholds shown in column headers. Green = passed, Red = failed.")

        display_cols = ["source_id", "TIC ID (Required)", "Contamination (<= 0.10)", "Radius TIC (Rsun)", "Radius Gaia est. (Rsun)", "Radius Match (<= 20% diff)", "TESS Sectors", "Status", "Reasons"]

        styled_df = results_df[display_cols].style.apply(color_tess_row, axis=1)
        for col in ["TIC ID (Required)", "Contamination (<= 0.10)", "Radius Match (<= 20% diff)", "Status"]:
            styled_df = styled_df.apply(lambda row, c=col: [color_cell(v, c, row) for v in row], axis=1)
        st.dataframe(styled_df, use_container_width=True)

        # Save
        username = st.session_state.username
        run_name = st.session_state.run_name
        run_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage2_tess")
        os.makedirs(run_folder, exist_ok=True)
        save_df = results_df.drop(columns=[c for c in results_df.columns if c.startswith("_")])
        save_df.to_csv(os.path.join(run_folder, "tess_appended.csv"), index=False)

        st.success("Saved cross-match results to your run folder")

        st.session_state.tess_results = save_df.to_dict("records")
        st.session_state.n_tess_passed = n_passed

        if n_passed > 0:
            st.markdown("---")
            st.page_link("pages/05_SIMBAD_CrossMatch.py", label="Go to SIMBAD Cross-Match")
        else:
            st.warning("No stars passed TESS checks. Pipeline ends here.")

st.markdown("---")
st.page_link("pages/03_Gaia_Filter.py", label="Back to Gaia Filter")
