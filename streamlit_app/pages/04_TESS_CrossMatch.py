"""
ExoX - Mod4: TESS Cross-Match
Real TIC catalog queries using astroquery
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

survivors_df = pd.DataFrame(st.session_state.gaia_survivors)
passed_gaia = survivors_df[survivors_df["_passed"] == True].copy()

if len(passed_gaia) == 0:
    st.warning("No stars passed Gaia filter.")
    st.stop()

st.title("TESS Cross-Match")
st.subheader("Query TESS Input Catalog for real stellar parameters")

st.markdown("""
Cross-matches Gaia survivors with the **TESS Input Catalog (TIC)**.
Retrieves Tmag, contamination ratio, and checks if the star is in TESS.
""")

st.markdown(f"**{len(passed_gaia)}** Gaia survivors to cross-match")

st.markdown("---")

n_total = len(passed_gaia)
tess_limit = min(20, n_total)  # Default
if n_total > 10:
        estimated_seconds = tess_limit * 2
        if estimated_seconds > 60:
            st.info(f"Estimated time: ~{estimated_seconds // 60} min {estimated_seconds % 60:.0f}s for {tess_limit} stars")
        else:
            st.info(f"Estimated time: ~{estimated_seconds:.0f}s for {tess_limit} stars")

if st.button("Run TESS Cross-Match", type="primary"):
    with st.spinner("Querying TESS Input Catalog..."):
        tess_results = []
        errors = []

        for _, star in passed_gaia.iterrows():
            source_id = star.get("source_id", "unknown")
            ra = star.get("_ra") or star.get("ra")
            dec = star.get("_dec") or star.get("dec")

            if ra is None or dec is None:
                errors.append(f"{source_id}: No coordinates")
                continue

            try:
                from astroquery.mast import Catalogs

                # Query TIC by coordinates — fixed syntax
                result = Catalogs.query_region(
                    f"{ra} {dec}",
                    catalog="TIC",
                    radius=0.005  # degrees (~18 arcsec)
                )

                if result is not None and len(result) > 0:
                    tic = result[0]

                    tic_id = tic.get("ID", tic.get("TICID", "N/A"))
                    tmag = tic.get("Tmag", tic.get("tmag", None))
                    contam = tic.get("contratio", tic.get("ContamRatio", None))

                    # Check contamination
                    if contam is not None and contam != "N/A":
                        try:
                            contam_val = float(contam)
                            passes_contam = contam_val <= 0.10
                        except (ValueError, TypeError):
                            passes_contam = True
                            contam = "N/A"
                    else:
                        passes_contam = True
                        contam = "N/A"

                    status = "PASSED" if passes_contam else "FAILED"
                    reason = "" if passes_contam else f"High contamination: {contam}"

                    tess_results.append({
                        "source_id": str(source_id),
                        "TIC ID": str(tic_id),
                        "Tmag": str(tmag) if tmag is not None else "N/A",
                        "Contamination (<= 0.10)": str(contam),
                        "Status": status,
                        "Reasons": reason if reason else "TESS match successful",
                        "_passed": passes_contam,
                        "_ra": ra,
                        "_dec": dec
                    })
                else:
                    tess_results.append({
                        "source_id": str(source_id),
                        "TIC ID": "NOT FOUND",
                        "Tmag": "N/A",
                        "Contamination (<= 0.10)": "N/A",
                        "Status": "NO MATCH",
                        "Reasons": "Not found in TIC",
                        "_passed": False,
                        "_ra": ra,
                        "_dec": dec
                    })

            except Exception as e:
                errors.append(f"{source_id}: {str(e)[:100]}")
                tess_results.append({
                    "source_id": str(source_id),
                    "TIC ID": "QUERY ERROR",
                    "Tmag": "N/A",
                    "Contamination (<= 0.10)": "N/A",
                    "Status": "ERROR",
                    "Reasons": str(e)[:80],
                    "_passed": False
                })

        # Display results
        if tess_results:
            results_df = pd.DataFrame(tess_results)
            passed = results_df[results_df["_passed"] == True]

            st.markdown("### TESS Cross-Match Results (Real MAST Archive)")
            col1, col2, col3 = st.columns(3)
            col1.metric("Cross-Matched", len(tess_results))
            col2.metric("Passed", len(passed))
            col3.metric("Failed/No Match", len(tess_results) - len(passed))

            def color_row(row):
                if row["Status"] == "PASSED":
                    return ['background-color: #d4edda; color: #155724'] * len(row)
                return ['background-color: #f8d7da; color: #721c24'] * len(row)

            display_cols = ["source_id", "TIC ID", "Tmag", "Contamination (<= 0.10)", "Status", "Reasons"]
            available_cols = [c for c in display_cols if c in results_df.columns]
            styled = results_df[available_cols].style.apply(color_row, axis=1)
            st.dataframe(styled, use_container_width=True)

            # Save
            username = st.session_state.username
            run_name = st.session_state.run_name
            run_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage2_tess")
            os.makedirs(run_folder, exist_ok=True)
            results_df.to_csv(os.path.join(run_folder, "tess_appended.csv"), index=False)

            st.session_state.tess_results = results_df.to_dict("records")
            st.session_state.n_tess_passed = len(passed)

            if len(passed) > 0:
                st.markdown("---")
                st.page_link("pages/05_SIMBAD_CrossMatch.py", label="GO TO SIMBAD CROSS-MATCH")

        if errors:
            st.markdown("---")
            st.markdown("### Query Issues")
            for e in errors[:5]:
                st.warning(e)

st.markdown("---")
st.page_link("pages/03_Gaia_Filter.py", label="Back to Gaia Filter")
