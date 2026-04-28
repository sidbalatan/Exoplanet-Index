"""
ExoX - Mod8: FITS Image Download (Stage 2: Exoplanet Probe)
Downloads real TESS cutout FITS images using coordinates from pipeline
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
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    LK_AVAILABLE = True
except ImportError:
    LK_AVAILABLE = False

st.set_page_config(page_title="FITS Download - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

if "certified_k_dwarfs" not in st.session_state or not st.session_state.certified_k_dwarfs:
    st.warning("No certified K-dwarfs. Complete Stage 1 first.")
    st.page_link("pages/10_WISE_AllWISE.py", label="Go to Stage 1")
    st.stop()

st.title("FITS Image Download")
st.subheader("Stage 2: Exoplanet Probe")

st.markdown("""
**Downloading real TESS data from the MAST archive.** Uses your target coordinates
to search for TESS observations. Not all stars have been observed by TESS.
""")

if not LK_AVAILABLE:
    st.error("Lightkurve not installed.")
    st.stop()

st.markdown(f"**{len(st.session_state.certified_k_dwarfs)}** stars to search")

# Get coordinates
coords_list = st.session_state.get("coords_list", [])
gaia_coords = st.session_state.get("gaia_coords", [])

# Merge coordinate sources
all_coords = coords_list + gaia_coords
coord_map = {}
for c in all_coords:
    if "ra" in c and "dec" in c:
        coord_map[str(c.get("ra", 0))] = c

st.markdown("---")

if st.button("Search TESS Archive", type="primary"):
    with st.spinner("Searching MAST for TESS data..."):
        fits_results = []
        
        for i, source_id in enumerate(st.session_state.certified_k_dwarfs):
            st.markdown(f"---")
            st.markdown(f"### Star {i+1}: {source_id}")

            # Try to find coordinates
            ra, dec = None, None
            
            # Check if source_id contains COORD_
            if source_id.startswith("COORD_"):
                parts = source_id.replace("COORD_", "").split("_")
                if len(parts) == 2:
                    try:
                        ra = float(parts[0])
                        dec = float(parts[1])
                    except ValueError:
                        pass
            
            # Check coord_map
            if ra is None:
                for key, c in coord_map.items():
                    ra = c.get("ra")
                    dec = c.get("dec")
                    break
            
            if ra is None or dec is None:
                st.warning("No coordinates available for this target.")
                fits_results.append({
                    "source_id": source_id,
                    "FITS Available": "NO COORDINATES",
                    "Status": "NO DATA",
                    "_confirmed": False
                })
                continue

            try:
                coord = SkyCoord(ra=ra, dec=dec, unit="deg")
                result = lk.search_tesscut(coord)
                
                if result is not None and len(result) > 0:
                    st.success(f"Found {len(result)} TESS observations!")
                    
                    try:
                        tpf = result[0].download()
                        
                        fig, ax = plt.subplots(figsize=(6, 6))
                        tpf.plot(frame=0, ax=ax, title=f"TESS Cutout - {source_id}")
                        st.pyplot(fig)
                        plt.close()
                        # Download button
                        fig.savefig('temp_fits.png', dpi=150, bbox_inches='tight')
                        with open('temp_fits.png', 'rb') as img_file:
                            st.download_button("DOWNLOAD FITS PLOT", img_file.read(), 
                                             f"{source_id}_fits.png", "image/png", key=f"dl_fits_{i}")
                        
                        fits_results.append({
                            "source_id": source_id,
                            "FITS Available": "YES",
                            "Status": "CONFIRMED",
                            "_confirmed": True,
                            "_ra": ra,
                            "_dec": dec
                        })
                        
                    except Exception as e:
                        st.warning(f"Download failed: {e}")
                        fits_results.append({
                            "source_id": source_id,
                            "FITS Available": "ERROR",
                            "Status": "ERROR",
                            "_confirmed": False
                        })
                else:
                    st.warning("No TESS data in MAST archive.")
                    fits_results.append({
                        "source_id": source_id,
                        "FITS Available": "NOT IN MAST",
                        "Status": "NO DATA",
                        "_confirmed": False
                    })
                    
            except Exception as e:
                st.error(f"Search failed: {e}")
                fits_results.append({
                    "source_id": source_id,
                    "FITS Available": "SEARCH ERROR",
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
            st.warning("No TESS data found for these targets.")

        st.dataframe(fits_df[["source_id", "FITS Available", "Status"]], use_container_width=True)

        if n_confirmed > 0:
            st.markdown("---")
            st.page_link("pages/07_LightCurve_Generation.py", label="GO TO LIGHT CURVE GENERATION")

st.markdown("---")
st.page_link("pages/10_WISE_AllWISE.py", label="Back to Stage 1")
