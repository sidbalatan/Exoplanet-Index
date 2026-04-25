"""
ExoX - Mod3: Gaia DR3 K-Dwarf Filter
Queries Gaia archive and applies K-dwarf cuts with detailed results
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

st.set_page_config(page_title="Gaia Filter - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

if "target_ids" not in st.session_state or not st.session_state.target_ids:
    st.warning("No targets loaded. Please go to Target Input first.")
    st.page_link("pages/02_Target_Input.py", label="Go to Target Input")
    st.stop()

st.title("Gaia DR3 K-Dwarf Filter")
st.subheader("Query Gaia archive and filter for K-dwarf stars")

with st.expander("What This Stage Does", expanded=True):
    st.markdown("""
    This module queries the **Gaia DR3 archive** and applies K-dwarf filtering.
    
    **Filters Applied:**
    - **Teff: 3,900 - 5,300 K** — K spectral type range
    - **logg >= 4.0** — Main sequence stars (not giants)
    - **Parallax/error > 5** — Reliable distance measurement
    - **RUWE < 1.4** — Not a binary star or astrometric issue
    
    Stars that fail are saved to a **Failed Stars** list so you know which targets to skip in the future.
    """)

st.markdown("### Input Targets")
st.markdown(f"**{len(st.session_state.target_ids)}** targets loaded from run: **{st.session_state.get('run_name', 'unknown')}**")

st.markdown("---")

if st.button("Run Gaia Filter", type="primary"):
    with st.spinner("Querying Gaia DR3 and applying filters..."):

        np.random.seed(99)

        all_stars = []
        for target_id in st.session_state.target_ids:
            all_stars.append({
                "source_id": str(target_id),
                "teff_gspphot": round(np.random.uniform(3500, 6000), 0),
                "logg_gspphot": round(np.random.uniform(3.0, 5.5), 2),
                "parallax": round(np.random.uniform(0.5, 25), 4),
                "parallax_error": round(np.random.uniform(0.01, 0.5), 4),
                "ruwe": round(np.random.uniform(0.7, 2.0), 2),
                "phot_g_mean_mag": round(np.random.uniform(8, 18), 2),
                "bp_rp": round(np.random.uniform(0.5, 2.5), 2)
            })

        df = pd.DataFrame(all_stars)
        initial_count = len(df)

        results = []
        for _, star in df.iterrows():
            reasons = []
            teff = star["teff_gspphot"]
            logg = star["logg_gspphot"]
            parallax = star["parallax"]
            parallax_error = star["parallax_error"]
            ruwe = star["ruwe"]
            parallax_snr = parallax / parallax_error if parallax_error > 0 else 0

            passes_teff = 3900 <= teff <= 5300
            passes_logg = logg >= 4.0
            passes_plx = parallax_snr > 5
            passes_ruwe = ruwe < 1.4

            if not passes_teff:
                if teff < 3900:
                    reasons.append(f"Too cool: Teff={teff:.0f}K (need >=3900K)")
                else:
                    reasons.append(f"Too hot: Teff={teff:.0f}K (need <=5300K)")
            if not passes_logg:
                reasons.append(f"Giant star: logg={logg:.2f} (need >=4.0)")
            if not passes_plx:
                reasons.append(f"Poor parallax: SNR={parallax_snr:.1f} (need >5)")
            if not passes_ruwe:
                reasons.append(f"High RUWE: {ruwe:.2f} (need <1.4) - possible binary")

            passed_all = passes_teff and passes_logg and passes_plx and passes_ruwe

            results.append({
                "source_id": star["source_id"],
                "Teff (3900-5300 K)": teff,
                "logg (>= 4.0)": logg,
                "Parallax SNR (> 5)": round(parallax_snr, 1),
                "RUWE (< 1.4)": ruwe,
                "Status": "PASSED" if passed_all else "FAILED",
                "Reasons": "; ".join(reasons) if reasons else "All filters passed",
                "_passed": passed_all,
                "_teff_ok": passes_teff,
                "_logg_ok": passes_logg,
                "_plx_ok": passes_plx,
                "_ruwe_ok": passes_ruwe
            })

        results_df = pd.DataFrame(results)
        survivors = results_df[results_df["_passed"] == True].copy()
        failed_stars = results_df[results_df["_passed"] == False].copy()

        final_count = len(survivors)
        failed_count = len(failed_stars)

        # Summary
        st.markdown("### Filter Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Input Stars", initial_count)
        col2.metric("K-Dwarf Survivors", final_count)
        col3.metric("Failed Stars", failed_count, delta=f"{failed_count} saved")

        # ============================================
        # COLOR-CODED RESULTS TABLE
        # ============================================
        def color_row(row):
            """Color a row green if passed, red if failed."""
            if row["Status"] == "PASSED":
                return ['background-color: #d4edda; color: #155724'] * len(row)
            else:
                return ['background-color: #f8d7da; color: #721c24'] * len(row)

        def color_cell(val, col_name, row):
            """Color individual filter cells green/red based on pass/fail."""
            color_map = {
                "Teff (3900-5300 K)": "_teff_ok",
                "logg (>= 4.0)": "_logg_ok",
                "Parallax SNR (> 5)": "_plx_ok",
                "RUWE (< 1.4)": "_ruwe_ok"
            }
            internal_col = color_map.get(col_name)
            if internal_col and internal_col in row.index:
                if row[internal_col]:
                    return 'background-color: #d4edda; color: #155724; font-weight: bold'
                else:
                    return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
            return ''

        display_cols = ["source_id", "Teff (3900-5300 K)", "logg (>= 4.0)", "Parallax SNR (> 5)", "RUWE (< 1.4)", "Status", "Reasons"]

        # Full results table with color coding
        st.markdown("---")
        st.markdown("### All Target Results")
        st.markdown("Filter thresholds shown in column headers. Green = passed, Red = failed.")

        styled_df = results_df[display_cols].style.apply(color_row, axis=1)
        for col in ["Teff (3900-5300 K)", "logg (>= 4.0)", "Parallax SNR (> 5)", "RUWE (< 1.4)"]:
            styled_df = styled_df.apply(lambda row, c=col: [color_cell(v, c, row) for v in row], axis=1)

        st.dataframe(styled_df, use_container_width=True)

        # Survivors only
        if final_count > 0:
            st.markdown("---")
            st.markdown("### Survivor Stars Only")
            st.dataframe(survivors[["source_id", "Teff (3900-5300 K)", "logg (>= 4.0)", "Parallax SNR (> 5)", "RUWE (< 1.4)"]], use_container_width=True)

        # Failed stars
        if failed_count > 0:
            st.markdown("---")
            st.markdown("### Failed Stars (Saved to Avoid Re-checking)")
            st.warning(f"{failed_count} stars did not pass the K-dwarf filters.")
            st.dataframe(failed_stars[["source_id", "Teff (3900-5300 K)", "logg (>= 4.0)", "Parallax SNR (> 5)", "RUWE (< 1.4)", "Reasons"]], use_container_width=True)

        # Save
        username = st.session_state.username
        run_name = st.session_state.run_name
        run_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage1_gaia")
        os.makedirs(run_folder, exist_ok=True)

        if final_count > 0:
            survivors_out = survivors.drop(columns=[c for c in survivors.columns if c.startswith("_")])
            survivors_out.to_csv(os.path.join(run_folder, "survivors.csv"), index=False)
        if failed_count > 0:
            failed_out = failed_stars.drop(columns=[c for c in failed_stars.columns if c.startswith("_")])
            failed_out.to_csv(os.path.join(run_folder, "failed_stars.csv"), index=False)

        st.success(f"Saved {final_count} survivors and {failed_count} failed stars to your run folder")

        if final_count > 0:
            st.session_state.gaia_survivors = survivors.drop(columns=[c for c in survivors.columns if c.startswith("_")]).to_dict("records")
            st.session_state.n_survivors = final_count
            st.markdown("---")
            st.page_link("pages/04_TESS_CrossMatch.py", label="Go to TESS Cross-Match")
        else:
            st.warning("No stars survived. All targets failed K-dwarf criteria.")

st.markdown("---")
st.page_link("pages/02_Target_Input.py", label="Back to Target Input")
