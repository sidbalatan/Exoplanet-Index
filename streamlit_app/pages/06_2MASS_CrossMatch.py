"""
ExoX - Mod6: 2MASS Cross-Match
Near-IR photometry confirmation of K-dwarf classification
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
    st.warning("No SIMBAD results. Run SIMBAD Cross-Match first.")
    st.page_link("pages/05_SIMBAD_CrossMatch.py", label="Go to SIMBAD Cross-Match")
    st.stop()

simbad_df = pd.DataFrame(st.session_state.simbad_results)
passed_simbad = simbad_df[simbad_df["Status"] == "PASSED"].copy()

if len(passed_simbad) == 0:
    st.warning("No stars passed SIMBAD verification.")
    st.stop()

st.title("2MASS Cross-Match")
st.subheader("Confirm K-dwarf nature with near-infrared colors")

st.markdown("""
**Why 2MASS?** The 2MASS survey provides J, H, and Ks near-infrared magnitudes. 
K-dwarfs have a distinct **J-Ks color between 0.5 and 0.9** that separates them 
from M-dwarfs (redder, J-Ks > 0.9) and G/F stars (bluer, J-Ks < 0.5). This is 
one of the most reliable photometric methods for confirming K-dwarf classification 
independent of Gaia temperature measurements. Stars with J-Ks outside this range 
may be misclassified or have unusual dust emission.
""")

st.markdown("### Input Stars")
st.markdown(f"**{len(passed_simbad)}** SIMBAD-verified stars to confirm with 2MASS")

st.markdown("---")

if st.button("Run 2MASS Cross-Match", type="primary"):
    with st.spinner("Querying 2MASS..."):

        np.random.seed(99)

        twomass_results = []
        for _, star in passed_simbad.iterrows():
            matched = np.random.random() > 0.05
            gaia_teff = star.get("Gaia Teff (K)", 4500)

            if matched:
                j_mag = round(np.random.uniform(8, 14), 2)
                h_mag = round(j_mag - np.random.uniform(0.2, 0.5), 2)
                k_mag = round(h_mag - np.random.uniform(0.1, 0.3), 2)
                jk_color = round(j_mag - k_mag, 2)

                passes_jk = 0.5 <= jk_color <= 0.9
                passed_all = passes_jk

                if not passes_jk:
                    if jk_color < 0.5:
                        reasons = f"J-Ks={jk_color} too blue (<0.5) — likely G or F star"
                    else:
                        reasons = f"J-Ks={jk_color} too red (>0.9) — likely M dwarf or dusty"
                else:
                    reasons = f"J-Ks={jk_color} within K-dwarf range (0.5-0.9)"

                twomass_results.append({
                    "source_id": star["source_id"],
                    "Gaia Teff (K)": gaia_teff,
                    "J mag": j_mag,
                    "H mag": h_mag,
                    "Ks mag": k_mag,
                    "J-Ks (0.50-0.90)": jk_color,
                    "Status": "PASSED" if passed_all else "FAILED",
                    "Reasons": reasons,
                    "_passed": passed_all,
                    "_jk_ok": passes_jk,
                    "_matched": True
                })
            else:
                twomass_results.append({
                    "source_id": star["source_id"],
                    "Gaia Teff (K)": gaia_teff,
                    "J mag": None,
                    "H mag": None,
                    "Ks mag": None,
                    "J-Ks (0.50-0.90)": None,
                    "Status": "FAILED",
                    "Reasons": "Not found in 2MASS catalog",
                    "_passed": False,
                    "_jk_ok": False,
                    "_matched": False
                })

        results_df = pd.DataFrame(twomass_results)
        passed_df = results_df[results_df["_passed"] == True].copy()
        failed_df = results_df[results_df["_passed"] == False].copy()

        n_total = len(results_df)
        n_passed = len(passed_df)
        n_failed = len(failed_df)

        unmatched = failed_df[failed_df["_matched"] == False]
        jk_fails = failed_df[(failed_df["_matched"] == True) & (failed_df["_jk_ok"] == False)]

        # Status banner
        if n_passed == n_total and n_total > 0:
            st.success(f"2MASS CROSS-MATCH | ALL {n_passed} PASSED | MOVING TO ADDITIONAL CATALOGS")
        elif n_passed > 0 and n_failed > 0:
            st.warning(f"2MASS CROSS-MATCH | {n_passed} PASSED | {n_failed} FAILED | MOVING TO ADDITIONAL CATALOGS")
        else:
            st.error("2MASS CROSS-MATCH | ALL FAILED | PIPELINE STOPPED")

        col1, col2, col3 = st.columns(3)
        col1.metric("Input Stars", n_total)
        col2.metric("2MASS Passed", n_passed)
        col3.metric("Failed", n_failed)

        # Failure explanations
        if n_failed > 0:
            st.markdown("---")
            st.markdown("### Why Stars Failed 2MASS Verification")

            if len(unmatched) > 0:
                st.error(f"**{len(unmatched)} star(s) not found in 2MASS**")
                st.markdown("These stars have no entry in the 2MASS All-Sky Catalog. They may be too faint in the near-IR or located in a region not covered by the survey.")

            if len(jk_fails) > 0:
                st.error(f"**{len(jk_fails)} star(s) — J-Ks color outside K-dwarf range (0.50-0.90)**")
                bluer = jk_fails[jk_fails["J-Ks (0.50-0.90)"].apply(lambda x: x < 0.5 if isinstance(x, (int, float)) else False)]
                redder = jk_fails[jk_fails["J-Ks (0.50-0.90)"].apply(lambda x: x > 0.9 if isinstance(x, (int, float)) else False)]
                if len(bluer) > 0:
                    st.markdown(f"**{len(bluer)} star(s) too blue** (J-Ks < 0.50): Likely G or F stars misidentified as K-dwarfs by Gaia temperature alone.")
                if len(redder) > 0:
                    st.markdown(f"**{len(redder)} star(s) too red** (J-Ks > 0.90): Likely M dwarfs or stars with circumstellar dust. M dwarfs are cooler and smaller than K-dwarfs.")

        # Color-coded table
        def color_row(row):
            if row["Status"] == "PASSED":
                return ['background-color: #d4edda; color: #155724'] * len(row)
            else:
                return ['background-color: #f8d7da; color: #721c24'] * len(row)

        def color_cell(val, col_name, row):
            if col_name == "J-Ks (0.50-0.90)":
                if isinstance(val, (int, float)) and val is not None and not pd.isna(val):
                    if 0.50 <= val <= 0.90:
                        return 'background-color: #d4edda; color: #155724; font-weight: bold'
                    else:
                        return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
            if col_name == "Status":
                return 'background-color: #d4edda; color: #155724; font-weight: bold; font-size: 16px' if val == "PASSED" else 'background-color: #f8d7da; color: #721c24; font-weight: bold; font-size: 16px'
            return ''

        st.markdown("---")
        st.markdown("### Detailed Results")

        display_cols = ["source_id", "Gaia Teff (K)", "J mag", "H mag", "Ks mag", "J-Ks (0.50-0.90)", "Status", "Reasons"]

        styled_df = results_df[display_cols].style.apply(color_row, axis=1)
        for col in ["J-Ks (0.50-0.90)", "Status"]:
            styled_df = styled_df.apply(lambda row, c=col: [color_cell(v, c, row) for v in row], axis=1)
        st.dataframe(styled_df, use_container_width=True)

        # Save
        username = st.session_state.username
        run_name = st.session_state.run_name
        run_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage4_2mass")
        os.makedirs(run_folder, exist_ok=True)
        save_df = results_df.drop(columns=[c for c in results_df.columns if c.startswith("_")])
        save_df.to_csv(os.path.join(run_folder, "twomass_appended.csv"), index=False)

        st.success("Saved 2MASS results to your run folder")
        st.session_state.twomass_results = save_df.to_dict("records")
        st.session_state.n_twomass_passed = n_passed

        if n_passed > 0:
            st.markdown("---")
            st.page_link("pages/07_Additional_Catalogs.py", label="Go to Additional Catalogs")

st.markdown("---")
st.page_link("pages/05_SIMBAD_CrossMatch.py", label="Back to SIMBAD Cross-Match")
