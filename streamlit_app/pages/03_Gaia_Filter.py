"""
ExoX - Mod3: Gaia DR3 K-Dwarf Filter
Real Gaia DR3 queries with actual K-dwarf filtering
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
    st.warning("No targets loaded. Go to Target Input first.")
    st.page_link("pages/02_Target_Input.py", label="Go to Target Input")
    st.stop()

st.title("Gaia DR3 K-Dwarf Filter")
st.subheader("Query the real Gaia archive and filter for K-dwarf stars")

with st.expander("What This Stage Does", expanded=True):
    st.markdown("""
    Queries the **Gaia DR3 archive** using `astroquery` and applies K-dwarf filters:
    - **Teff: 3,900-5,300 K**
    - **logg >= 4.0**
    - **Parallax/error > 5**
    - **RUWE < 1.4**
    """)

st.markdown(f"**{len(st.session_state.target_ids)}** targets loaded")

st.markdown("---")

if st.button("Query Gaia DR3 & Filter", type="primary"):
    with st.spinner("Querying Gaia DR3 archive..."):

        all_results = []
        errors = []

        for target_id in st.session_state.target_ids[:20]:  # Limit to 20 for speed
            
            # Extract Gaia ID or coordinates
            gaia_id = None
            ra, dec = None, None
            
            if target_id.startswith("COORD_"):
                parts = target_id.replace("COORD_", "").split("_")
                if len(parts) == 2:
                    try:
                        ra = float(parts[0])
                        dec = float(parts[1])
                    except ValueError:
                        pass
            elif target_id.startswith("TIC_"):
                pass  # Skip TIC for Gaia query
            elif target_id.isdigit() and len(target_id) >= 18:
                gaia_id = target_id

            try:
                if gaia_id:
                    # Query by Gaia DR3 ID
                    from astroquery.gaia import Gaia
                    query = f"""
                    SELECT source_id, ra, dec, teff_gspphot, logg_gspphot,
                           parallax, parallax_error, phot_g_mean_mag, bp_rp, ruwe, mh_gspphot
                    FROM gaiadr3.gaia_source
                    WHERE source_id = {gaia_id}
                    """
                    job = Gaia.launch_job_async(query)
                    result = job.get_results()
                    df = result.to_pandas()
                    
                elif ra is not None and dec is not None:
                    # Query by coordinates
                    from astroquery.gaia import Gaia
                    query = f"""
                    SELECT TOP 1 source_id, ra, dec, teff_gspphot, logg_gspphot,
                           parallax, parallax_error, phot_g_mean_mag, bp_rp, ruwe, mh_gspphot
                    FROM gaiadr3.gaia_source
                    WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra}, {dec}, 0.001))
                    """
                    job = Gaia.launch_job_async(query)
                    result = job.get_results()
                    df = result.to_pandas()
                else:
                    continue

                if len(df) > 0:
                    star = df.iloc[0]
                    teff = star["teff_gspphot"]
                    logg = star["logg_gspphot"]
                    plx = star["parallax"]
                    plx_err = star["parallax_error"]
                    ruwe = star["ruwe"]
                    plx_snr = plx / plx_err if plx_err > 0 else 0

                    passes_teff = 3900 <= teff <= 5300 if pd.notna(teff) else False
                    passes_logg = logg >= 4.0 if pd.notna(logg) else False
                    passes_plx = plx_snr > 5
                    passes_ruwe = ruwe < 1.4 if pd.notna(ruwe) else False
                    passed_all = passes_teff and passes_logg and passes_plx and passes_ruwe

                    reasons = []
                    if not passes_teff:
                        reasons.append(f"Teff={teff:.0f}K (need 3900-5300)")
                    if not passes_logg:
                        reasons.append(f"logg={logg:.2f} (need >=4.0)")
                    if not passes_plx:
                        reasons.append(f"Parallax SNR={plx_snr:.1f} (need >5)")
                    if not passes_ruwe:
                        reasons.append(f"RUWE={ruwe:.2f} (need <1.4)")

                    all_results.append({
                        "source_id": str(star["source_id"]),
                        "Teff (3900-5300 K)": teff if pd.notna(teff) else "N/A",
                        "logg (>= 4.0)": logg if pd.notna(logg) else "N/A",
                        "Parallax SNR (> 5)": round(plx_snr, 1),
                        "RUWE (< 1.4)": ruwe if pd.notna(ruwe) else "N/A",
                        "Status": "PASSED" if passed_all else "FAILED",
                        "Reasons": "; ".join(reasons) if reasons else "All filters passed",
                        "_passed": passed_all,
                        "_ra": star["ra"],
                        "_dec": star["dec"]
                    })
                else:
                    errors.append(f"{target_id}: Not found in Gaia")

            except Exception as e:
                errors.append(f"{target_id}: {str(e)[:100]}")

        # Show results
        if all_results:
            results_df = pd.DataFrame(all_results)
            passed = results_df[results_df["_passed"] == True]
            
            st.markdown("### Results from Real Gaia Archive")
            col1, col2, col3 = st.columns(3)
            col1.metric("Queried", len(all_results))
            col2.metric("K-Dwarfs Found", len(passed))
            col3.metric("Failed", len(results_df) - len(passed))
            
            # Color-coded table
            def color_row(row):
                if row["Status"] == "PASSED":
                    return ['background-color: #d4edda; color: #155724'] * len(row)
                return ['background-color: #f8d7da; color: #721c24'] * len(row)
            
            display_cols = ["source_id", "Teff (3900-5300 K)", "logg (>= 4.0)", "Parallax SNR (> 5)", "RUWE (< 1.4)", "Status", "Reasons"]
            styled = results_df[display_cols].style.apply(color_row, axis=1)
            st.dataframe(styled, use_container_width=True)
            
            # Save
            username = st.session_state.username
            run_name = st.session_state.run_name
            run_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage1_gaia")
            os.makedirs(run_folder, exist_ok=True)
            results_df.to_csv(os.path.join(run_folder, "survivors.csv"), index=False)
            
            st.session_state.gaia_survivors = results_df.to_dict("records")
            st.session_state.n_survivors = len(passed)
            
            if len(passed) > 0:
                st.markdown("---")
                st.page_link("pages/04_TESS_CrossMatch.py", label="GO TO TESS CROSS-MATCH")
        
        if errors:
            st.markdown("---")
            st.markdown("### Query Errors")
            for e in errors[:5]:
                st.warning(e)

st.markdown("---")
st.page_link("pages/02_Target_Input.py", label="Back to Target Input")
