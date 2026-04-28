"""
ExoX - Mod8: FITS Image Download (Stage 2: Exoplanet Probe)
Downloads real TESS cutout FITS images using lightkurve
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt

try:
    import lightkurve as lk
    LK_AVAILABLE = True
except ImportError:
    LK_AVAILABLE = False

st.set_page_config(page_title="FITS Download - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

if "certified_k_dwarfs" not in st.session_state or not st.session_state.certified_k_dwarfs:
    st.warning("No certified K-dwarfs. Complete Stage 1 first.")
    st.page_link("pages/07_Additional_Catalogs.py", label="Go to Stage 1")
    st.stop()

st.title("FITS Image Download")
st.subheader("Stage 2: Exoplanet Probe — Real TESS Data")

st.markdown("""
**Downloading real TESS data from the MAST archive.** This module uses `lightkurve` 
to search for TESS observations of your certified K-dwarfs.

**Note:** Not all stars have been observed by TESS. If the MAST archive does not 
contain data for your target, it simply means TESS has not observed that region yet.
""")

if not LK_AVAILABLE:
    st.error("Lightkurve is not installed. Run: pip install lightkurve")
    st.stop()

st.markdown("### Certified K-Dwarfs Ready for Imaging")
st.markdown(f"**{len(st.session_state.certified_k_dwarfs)}** stars to search")

# Get coordinates from previous results if available
coords_available = False
if "additional_results" in st.session_state:
    add_df = pd.DataFrame(st.session_state.additional_results)
    if "ra" in add_df.columns and "dec" in add_df.columns:
        coords_available = True

st.markdown("---")

if st.button("Search TESS Archive", type="primary"):
    with st.spinner("Searching MAST for TESS data..."):

        fits_results = []
        
        for i, source_id in enumerate(st.session_state.certified_k_dwarfs):
            st.markdown(f"---")
            st.markdown(f"### Star {i+1}: {source_id}")

            try:
                # Try to search by Gaia DR3 ID
                search_result = lk.search_tesscut(f"Gaia DR3 {source_id}")
                
                if search_result is not None and len(search_result) > 0:
                    st.success(f"Found {len(search_result)} TESS observations!")
                    
                    for j, obs in enumerate(search_result):
                        sector = obs.sector if hasattr(obs, 'sector') else 'N/A'
                        camera = obs.camera if hasattr(obs, 'camera') else 'N/A'
                        st.markdown(f"- Sector {sector}, Camera {camera}")
                    
                    try:
                        tpf = search_result[0].download()
                        
                        fig, ax = plt.subplots(figsize=(6, 6))
                        tpf.plot(frame=0, ax=ax, title=f"TESS Cutout - {source_id}")
                        st.pyplot(fig)
                        plt.close()
                        
                        fits_results.append({
                            "source_id": source_id,
                            "FITS Available": "YES",
                            "N Observations": len(search_result),
                            "Visual Confirmed": "YES",
                            "Status": "CONFIRMED",
                            "_confirmed": True
                        })
                        
                    except Exception as e:
                        st.warning(f"Download failed: {e}")
                        fits_results.append({
                            "source_id": source_id,
                            "FITS Available": "FOUND BUT ERROR",
                            "N Observations": len(search_result),
                            "Status": "ERROR",
                            "_confirmed": False
                        })
                else:
                    st.warning("No TESS data in MAST archive for this target.")
                    st.caption("This star has not been observed by TESS or is outside the mission footprint.")
                    
                    fits_results.append({
                        "source_id": source_id,
                        "FITS Available": "NOT IN MAST",
                        "N Observations": 0,
                        "Status": "NO DATA",
                        "_confirmed": False
                    })
                    
            except Exception as e:
                st.error(f"Search failed: {e}")
                fits_results.append({
                    "source_id": source_id,
                    "FITS Available": "SEARCH ERROR",
                    "N Observations": 0,
                    "Status": "ERROR",
                    "_confirmed": False
                })

        # Save
        fits_df = pd.DataFrame(fits_results)
        confirmed_df = fits_df[fits_df["_confirmed"] == True]
        n_confirmed = len(confirmed_df)

        username = st.session_state.username
        run_name = st.session_state.run_name
        fits_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage6_fits")
        os.makedirs(fits_folder, exist_ok=True)
        fits_df.to_csv(os.path.join(fits_folder, "fits_download.csv"), index=False)

        st.session_state.fits_results = fits_df.to_dict("records")
        st.session_state.n_fits_confirmed = n_confirmed

        st.markdown("---")
        st.markdown("## FITS Download Summary")
        
        if n_confirmed > 0:
            st.success(f"{n_confirmed} STARS HAVE REAL TESS DATA")
        else:
            st.warning("No TESS data found in MAST for these targets.")

        st.dataframe(fits_df[["source_id", "FITS Available", "Status"]], use_container_width=True)

        if n_confirmed > 0:
            st.markdown("---")
            st.page_link("pages/09_LightCurve_Generation.py", label="GO TO LIGHT CURVE GENERATION")

st.markdown("---")
st.page_link("pages/07_Additional_Catalogs.py", label="Back to Stage 1")
