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

if "twomass_results" not in st.session_state or not st.session_state.twomass_results:
    st.warning("No 2MASS results. Run 2MASS first.")
    st.page_link("pages/06_2MASS_CrossMatch.py", label="Go to 2MASS")
    st.stop()

twomass_df = pd.DataFrame(st.session_state.twomass_results)
passed_twomass = twomass_df[twomass_df["_passed"] == True].copy()

if len(passed_twomass) == 0:
    st.warning("No stars passed 2MASS.")
    st.stop()

st.title("WISE/ALLWISE Cross-Match")
st.subheader("Final K-Dwarf Validation — Infrared Excess Detection")

st.markdown("""
**What This Stage Does:**
Queries the **WISE/ALLWISE** catalog for mid-infrared photometry (W1, W2 bands).
Detects infrared excess that could indicate:
- Warm circumstellar dust (debris disk)
- Unresolved companion star
- Unusual stellar activity

**Survival Criterion:**
- **W1-W2 < 0.5** — No significant infrared excess
""")

# APASS/UCAC4 notice
st.info("""
**Additional Catalogs Available Upon Request**

APASS (optical B, V magnitudes) and UCAC4 (proper motion verification) are available 
for targets that require further investigation. These catalogs provide independent 
confirmation of stellar classification and motion.

To request APASS/UCAC4 analysis for your targets, contact the ExoX editorial team at:
**exox-pipeline@proton.me**

Requests are reviewed within 48 hours. Priority is given to targets with conflicting 
classifications across Gaia, SIMBAD, and 2MASS.
""")

st.markdown(f"**{len(passed_twomass)}** stars to verify with WISE")

st.markdown("---")

if st.button("Run WISE/ALLWISE Cross-Match", type="primary"):
    with st.spinner("Querying WISE/ALLWISE catalog..."):

        wise_results = []

        for _, star in passed_twomass.iterrows():
            source_id = star.get("source_id", "unknown")
            ra = star.get("_ra")
            dec = star.get("_dec")

            if ra is None or dec is None:
                continue

            try:
                from astroquery.ipac.irsa import Irsa

                # Query ALLWISE catalog
                result = Irsa.query_region(
                    f"{ra} {dec}",
                    catalog="allwise_p3as_psd",
                    radius="0:0:3"
                )

                if result is not None and len(result) > 0:
                    row = result[0]
                    w1 = row.get("w1mpro")
                    w2 = row.get("w2mpro")

                    if w1 is not None and w2 is not None:
                        w1_w2 = float(w1) - float(w2)
                        passes_wise = w1_w2 < 0.5

                        wise_results.append({
                            "source_id": str(source_id),
                            "W1 mag": round(float(w1), 2),
                            "W2 mag": round(float(w2), 2),
                            "W1-W2 (< 0.50)": round(w1_w2, 2),
                            "IR Excess?": "YES" if not passes_wise else "NO",
                            "Status": "PASSED" if passes_wise else "FAILED",
                            "Reasons": f"W1-W2={w1_w2:.2f} — IR excess detected" if not passes_wise else "Clean — no IR excess",
                            "_passed": passes_wise,
                            "_ra": ra,
                            "_dec": dec
                        })
                    else:
                        wise_results.append({
                            "source_id": str(source_id),
                            "W1-W2 (< 0.50)": "N/A",
                            "Status": "INCOMPLETE",
                            "Reasons": "Missing WISE photometry",
                            "_passed": False
                        })
                else:
                    wise_results.append({
                        "source_id": str(source_id),
                        "W1-W2 (< 0.50)": "N/A",
                        "Status": "NOT FOUND",
                        "Reasons": "Not in WISE/ALLWISE",
                        "_passed": False
                    })

            except Exception as e:
                wise_results.append({
                    "source_id": str(source_id),
                    "W1-W2 (< 0.50)": "ERROR",
                    "Status": "ERROR",
                    "Reasons": str(e)[:80],
                    "_passed": False
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
                    st.success(f"{n_passed} STARS CERTIFIED AS K-DWARFS | {n_total - n_passed} FAILED")
                
                for _, star in passed.iterrows():
                    st.markdown(f"**{star['source_id']}** has passed all 5 validation stages and is now a Certified K-Dwarf.")

            # Summary
            col1, col2, col3 = st.columns(3)
            col1.metric("Input Stars", n_total)
            col2.metric("Certified K-Dwarfs", n_passed)
            col3.metric("Failed", n_total - n_passed)

            # Color-coded table
            def color_row(row):
                if row["Status"] == "PASSED":
                    return ['background-color: #d4edda; color: #155724'] * len(row)
                return ['background-color: #f8d7da; color: #721c24'] * len(row)

            display_cols = ["source_id", "W1 mag", "W2 mag", "W1-W2 (< 0.50)", "IR Excess?", "Status", "Reasons"]
            styled = results_df[display_cols].style.apply(color_row, axis=1)
            st.dataframe(styled, use_container_width=True)

            # Save
            username = st.session_state.username
            run_name = st.session_state.run_name
            run_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage5_additional")
            os.makedirs(run_folder, exist_ok=True)
            save_df = results_df.drop(columns=[c for c in results_df.columns if c.startswith("_")])
            save_df.to_csv(os.path.join(run_folder, "wise_appended.csv"), index=False)
            
            if n_passed > 0:
                certified = passed[["source_id"]].copy()
                certified.to_csv(os.path.join(run_folder, "certified_k_dwarfs.csv"), index=False)

            st.session_state.additional_results = save_df.to_dict("records")
            st.session_state.n_additional_passed = n_passed
            st.session_state.certified_k_dwarfs = passed["source_id"].tolist() if n_passed > 0 else []

            # Transition to Stage 2
            if n_passed > 0:
                st.markdown("---")
                st.markdown("## PROCEED TO STAGE 2: EXOPLANET PROBE")
                st.markdown("""
                Your certified K-dwarfs are ready for exoplanet detection:
                1. **FITS Images** — Visual confirmation from TESS
                2. **Light Curves** — Real TESS photometry
                3. **Transit Detection** — BLS periodogram and phase folding
                """)
                st.page_link("pages/08_FITS_Download.py", label="GO TO FITS IMAGE DOWNLOAD (STAGE 2)")

st.markdown("---")
st.page_link("pages/06_2MASS_CrossMatch.py", label="Back to 2MASS Cross-Match")
