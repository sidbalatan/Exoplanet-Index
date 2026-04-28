"""
ExoX - Mod3: Gaia DR3 K-Dwarf Filter
Real Gaia queries using coordinates from uploaded targets
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
st.subheader("Query Gaia archive by coordinates and filter for K-dwarfs")

with st.expander("What This Stage Does", expanded=True):
    st.markdown("""
    Queries **Gaia DR3** by coordinates (RA, Dec) and applies K-dwarf filters:
    - **Teff: 3,900-5,300 K** — K spectral type
    - **logg >= 4.0** — Main sequence, not giant
    - **Parallax SNR > 5** — Reliable distance
    - **RUWE < 1.4** — Not a binary star
    """)

st.markdown(f"**{len(st.session_state.target_ids)}** targets loaded")

# Get coordinates from session
coords_list = st.session_state.get("coords_list", [])

st.markdown("---")

if len(st.session_state.target_ids) > 50:
    st.warning(f"Processing {len(st.session_state.target_ids)} targets. This may take several minutes.")
elif len(st.session_state.target_ids) > 20:
    st.info(f"Processing {len(st.session_state.target_ids)} targets. Estimated time: ~1-2 minutes.")

if st.button("Query Gaia DR3 & Filter", type="primary"):
    with st.spinner("Querying Gaia DR3 by coordinates..."):
        
        all_results = []
        errors = []
        queried = 0
        
        # Use coordinates list if available, otherwise parse target_ids
        targets_to_query = []
        
        if coords_list:
            for i, target_id in enumerate(st.session_state.target_ids):
                if i < len(coords_list):
                    targets_to_query.append({
                        "target_id": target_id,
                        "ra": coords_list[i].get("ra"),
                        "dec": coords_list[i].get("dec")
                    })
        else:
            # Parse target_ids for COORD_ format
            for target_id in st.session_state.target_ids:
                if target_id.startswith("COORD_"):
                    parts = target_id.replace("COORD_", "").split("_")
                    if len(parts) == 2:
                        try:
                            ra = float(parts[0])
                            dec = float(parts[1])
                            targets_to_query.append({"target_id": target_id, "ra": ra, "dec": dec})
                        except ValueError:
                            pass
                elif target_id.isdigit() and len(target_id) >= 18:
                    targets_to_query.append({"target_id": target_id, "ra": None, "dec": None})
        
        # Limit to 20 for speed
        for target in targets_to_query[:500]:
            target_id = target["target_id"]
            ra = target.get("ra")
            dec = target.get("dec")
            
            if ra is None or dec is None:
                errors.append(f"{str(target_id)[:30]}: Missing coordinates")
                continue
            
            queried += 1
            
            try:
                from astroquery.gaia import Gaia
                
                # Query by coordinates (0.001 deg ~ 3.6 arcsec)
                query = f"""
                SELECT TOP 1 source_id, ra, dec, teff_gspphot, logg_gspphot,
                       parallax, parallax_error, phot_g_mean_mag, bp_rp, ruwe, mh_gspphot
                FROM gaiadr3.gaia_source
                WHERE 1=CONTAINS(
                    POINT('ICRS', ra, dec),
                    CIRCLE('ICRS', {ra}, {dec}, 0.005)
                )
                """
                
                job = Gaia.launch_job_async(query)
                result = job.get_results()
                df = result.to_pandas()
                
                if len(df) > 0:
                    star = df.iloc[0]
                    teff = star["teff_gspphot"] if pd.notna(star["teff_gspphot"]) else None
                    logg = star["logg_gspphot"] if pd.notna(star["logg_gspphot"]) else None
                    plx = star["parallax"] if pd.notna(star["parallax"]) else 0
                    plx_err = star["parallax_error"] if pd.notna(star["parallax_error"]) else 0.01
                    ruwe = star["ruwe"] if pd.notna(star["ruwe"]) else 99
                    plx_snr = plx / plx_err if plx_err > 0 else 0
                    
                    passes_teff = (teff is not None and 3900 <= teff <= 5300)
                    passes_logg = (logg is not None and logg >= 4.0)
                    passes_plx = plx_snr > 5
                    passes_ruwe = (ruwe is not None and ruwe < 1.4)
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
                        "Input ID": str(target_id)[:30],
                        "Teff (3900-5300 K)": f"{teff:.0f}" if teff else "N/A",
                        "logg (>= 4.0)": f"{logg:.2f}" if logg else "N/A",
                        "Parallax SNR (> 5)": round(plx_snr, 1),
                        "RUWE (< 1.4)": f"{ruwe:.2f}" if ruwe else "N/A",
                        "Status": "PASSED" if passed_all else "FAILED",
                        "Reasons": "; ".join(reasons) if reasons else "All filters passed",
                        "_passed": passed_all,
                        "_ra": star["ra"],
                        "_dec": star["dec"]
                    })
                else:
                    errors.append(f"{str(target_id)[:30]}: Not found in Gaia at these coordinates")
                    
            except Exception as e:
                errors.append(f"{str(target_id)[:30]}: {str(e)[:80]}")
        
        # Display results
        if all_results:
            results_df = pd.DataFrame(all_results)
            passed = results_df[results_df["_passed"] == True]
            
            st.markdown(f"### Results ({queried} queried, {len(passed)} K-dwarfs found)")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Queried", queried)
            col2.metric("K-Dwarfs", len(passed))
            col3.metric("Failed/Not Found", len(results_df) - len(passed))
            
            def color_row(row):
                if row["Status"] == "PASSED":
                    return ['background-color: #d4edda; color: #155724'] * len(row)
                return ['background-color: #f8d7da; color: #721c24'] * len(row)
            
            display_cols = ["source_id", "Input ID", "Teff (3900-5300 K)", "logg (>= 4.0)", "Parallax SNR (> 5)", "RUWE (< 1.4)", "Status", "Reasons"]
            available_cols = [c for c in display_cols if c in results_df.columns]
            styled = results_df[available_cols].style.apply(color_row, axis=1)
            st.dataframe(styled, use_container_width=True)
            
            # Save
            username = st.session_state.username
            run_name = st.session_state.run_name
            run_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage1_gaia")
            os.makedirs(run_folder, exist_ok=True)
            results_df.to_csv(os.path.join(run_folder, "survivors.csv"), index=False)
            
            st.session_state.gaia_survivors = results_df.to_dict("records")
            st.session_state.n_survivors = len(passed)
            st.session_state.coords_list = coords_list  # Pass forward
            
            if len(passed) > 0:
                st.markdown("---")
                st.success(f"{len(passed)} stars passed Gaia filters")
                st.page_link("pages/04_TESS_CrossMatch.py", label="GO TO TESS CROSS-MATCH")
            else:
                st.warning("No stars passed all Gaia filters.")
                st.markdown("You can still proceed with the stars that were found, or try different targets.")
            
            # Always show navigation
            if len(all_results) > 0:
                st.markdown("---")
                st.page_link("pages/04_TESS_CrossMatch.py", label="GO TO TESS CROSS-MATCH (USE ALL FOUND STARS)")
        
        if errors:
            st.markdown("---")
            st.markdown("### Query Notes")
            for e in errors[:5]:
                st.info(e)

st.markdown("---")
st.page_link("pages/02_Target_Input.py", label="Back to Target Input")
