"""
ExoX - Mod9: Light Curve Generation (Stage 2: Exoplanet Probe)
Real TESS light curves using coordinates from pipeline
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

st.set_page_config(page_title="Light Curves - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

if "fits_results" not in st.session_state or not st.session_state.fits_results:
    st.warning("No FITS results. Run FITS Download first.")
    st.page_link("pages/08_FITS_Download.py", label="Go to FITS Download")
    st.stop()

fits_df = pd.DataFrame(st.session_state.fits_results)
confirmed = fits_df[fits_df["Status"] == "CONFIRMED"].copy()

if len(confirmed) == 0:
    st.warning("No stars with TESS data.")
    st.stop()

if not LK_AVAILABLE:
    st.error("Lightkurve not installed.")
    st.stop()

st.title("Light Curve Generation")
st.subheader("Stage 2: Exoplanet Probe — Real TESS Photometry")

st.markdown("**Downloading real TESS photometry from MAST. Daily limit: 12.**")

# Daily limit
username = st.session_state.username
today = datetime.now().strftime("%Y-%m-%d")
usage_file = f"users/{username}/lightcurve_usage.json"

if os.path.exists(usage_file):
    with open(usage_file, 'r') as f:
        usage = json.load(f)
    if usage.get("date") != today:
        usage = {"date": today, "count": 0}
else:
    usage = {"date": today, "count": 0}

remaining = 12 - usage["count"]
if remaining <= 0:
    st.error("Daily limit reached.")
    st.stop()

st.info(f"Daily limit: {usage['count']} used, {remaining} remaining")
max_stars = min(remaining, len(confirmed))

st.markdown("---")

if st.button("Generate Real Light Curves", type="primary"):
    with st.spinner("Downloading TESS photometry..."):
        lc_results = []
        current_usage = usage["count"]
        
        for i, (_, star) in enumerate(confirmed.head(max_stars).iterrows()):
            if current_usage >= 12:
                break
            
            source_id = star["source_id"]
            ra = star.get("_ra")
            dec = star.get("_dec")
            
            st.markdown(f"---")
            st.markdown(f"### Star {i+1}: {source_id}")
            
            if ra is None or dec is None:
                st.warning("No coordinates available.")
                continue
            
            try:
                coord = SkyCoord(ra=ra, dec=dec, unit="deg")
                search = lk.search_lightcurve(coord, mission="TESS")
                
                if search and len(search) > 0:
                    st.success(f"Found light curve — downloading...")
                    lc = search[0].download()
                    lc = lc.remove_nans()
                    lc_flat = lc.flatten(window_length=101)
                    lc_clean = lc_flat.remove_outliers(sigma=5)
                    
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
                    lc.scatter(ax=ax1, s=2, alpha=0.5, c='gray')
                    ax1.set_title(f'Raw TESS Light Curve - {source_id}')
                    ax1.set_xlabel('Time (BJD)')
                    ax1.set_ylabel('Flux')
                    
                    lc_clean.scatter(ax=ax2, s=2, alpha=0.5, c='black')
                    ax2.set_title('Detrended & Normalized')
                    ax2.set_xlabel('Time (BJD)')
                    ax2.set_ylabel('Normalized Flux')
                    ax2.axhline(1.0, color='r', linestyle='--')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()
                    # Download button
                    fig.savefig('temp_lc.png', dpi=150, bbox_inches='tight')
                    with open('temp_lc.png', 'rb') as img_file:
                        st.download_button("DOWNLOAD LIGHT CURVE", img_file.read(),
                                         f"{source_id}_lightcurve.png", "image/png", key=f"dl_lc_{i}")
                    
                    # Save
                    lc_folder = os.path.join("users", username, "pipeline_runs", 
                                            st.session_state.run_name, "lightcurves")
                    os.makedirs(lc_folder, exist_ok=True)
                    
                    lc_data = pd.DataFrame({
                        "time": lc_clean.time.value,
                        "flux": lc_clean.flux.value
                    })
                    lc_data.to_csv(os.path.join(lc_folder, f"{source_id}_lightcurve.csv"), index=False)
                    
                    st.success(f"Saved: {len(lc_clean.flux)} points over {lc_clean.time.value[-1] - lc_clean.time.value[0]:.1f} days")
                    
                    lc_results.append({
                        "source_id": source_id,
                        "N Points": len(lc_clean.flux),
                        "Status": "REAL TESS DATA"
                    })
                    
                else:
                    st.warning("No light curves in MAST.")
                    lc_results.append({"source_id": source_id, "Status": "NOT IN MAST"})
                    
            except Exception as e:
                st.error(f"Error: {e}")
                lc_results.append({"source_id": source_id, "Status": "FAILED"})
            
            current_usage += 1
            usage["count"] = current_usage
            usage["date"] = today
            with open(usage_file, 'w') as f:
                json.dump(usage, f)

        lc_df = pd.DataFrame(lc_results)
        st.session_state.lightcurve_results = lc_df.to_dict("records")
        
        n_real = len(lc_df[lc_df["Status"] == "REAL TESS DATA"])
        st.success(f"Generated {n_real} real TESS light curves")
        
        st.markdown("---")
        st.page_link("pages/10_Transit_Detection.py", label="GO TO TRANSIT DETECTION")

st.markdown("---")
st.page_link("pages/08_FITS_Download.py", label="Back to FITS Download")
