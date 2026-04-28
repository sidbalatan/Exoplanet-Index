"""
ExoX - Mod9: Light Curve Generation (Stage 2: Exoplanet Probe)
Generates real TESS light curves using lightkurve — no simulated fallback
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

st.set_page_config(page_title="Light Curves - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

if "fits_results" not in st.session_state or not st.session_state.fits_results:
    st.warning("No FITS images. Run FITS Download first.")
    st.page_link("pages/08_FITS_Download.py", label="Go to FITS Download")
    st.stop()

fits_df = pd.DataFrame(st.session_state.fits_results)
confirmed = fits_df[fits_df["Status"] == "CONFIRMED"].copy()

if len(confirmed) == 0:
    st.warning("No stars with TESS data available. Cannot generate light curves.")
    st.stop()

if not LK_AVAILABLE:
    st.error("Lightkurve is not installed.")
    st.stop()

st.title("Light Curve Generation")
st.subheader("Stage 2: Exoplanet Probe — Real TESS Photometry")

st.markdown("""
**Generating real light curves from the MAST archive.** This module downloads 
actual TESS photometry, detrends, and normalizes the data.

**Daily limit: 12 light curves per user.**
""")

st.markdown(f"**{len(confirmed)}** stars with TESS data")

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
    st.error("Daily limit reached. Try again tomorrow.")
    st.stop()

st.info(f"Daily limit: {usage['count']} used, {remaining} remaining")

max_stars = min(remaining, len(confirmed))
st.markdown(f"**{max_stars}** star(s) available today.")

st.markdown("---")

if st.button("Generate Real Light Curves", type="primary"):
    with st.spinner("Downloading TESS photometry from MAST..."):

        lc_results = []
        current_usage = usage["count"]
        stars_to_process = confirmed.head(max_stars)

        for i, (_, star) in enumerate(stars_to_process.iterrows()):
            if current_usage >= 12:
                break

            source_id = star["source_id"]
            st.markdown(f"---")
            st.markdown(f"### Star {i+1}: {source_id}")

            try:
                search = lk.search_lightcurve(f"Gaia DR3 {source_id}", mission="TESS")
                
                if search is not None and len(search) > 0:
                    st.success(f"Found {len(search)} TESS light curves")
                    
                    lc = search[0].download()
                    lc = lc.remove_nans()
                    lc_flat = lc.flatten(window_length=101)
                    lc_clean = lc_flat.remove_outliers(sigma=5)
                    
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
                    
                    lc.scatter(ax=ax1, s=2, alpha=0.5, c='gray', label='Raw')
                    ax1.set_title(f'Raw TESS Light Curve - {source_id}')
                    ax1.set_xlabel('Time (BJD)')
                    ax1.set_ylabel('Flux')
                    ax1.legend()
                    
                    lc_clean.scatter(ax=ax2, s=2, alpha=0.5, c='black', label='Detrended')
                    ax2.set_title(f'Detrended & Normalized - {source_id}')
                    ax2.set_xlabel('Time (BJD)')
                    ax2.set_ylabel('Normalized Flux')
                    ax2.axhline(1.0, color='r', linestyle='--')
                    ax2.legend()
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()
                    
                    lc_folder = os.path.join("users", username, "pipeline_runs", 
                                            st.session_state.run_name, "lightcurves")
                    os.makedirs(lc_folder, exist_ok=True)
                    
                    lc_data = pd.DataFrame({
                        "time": lc_clean.time.value,
                        "flux": lc_clean.flux.value,
                        "flux_err": lc_clean.flux_err.value if hasattr(lc_clean, 'flux_err') else np.zeros(len(lc_clean.flux))
                    })
                    lc_data.to_csv(os.path.join(lc_folder, f"{source_id}_lightcurve.csv"), index=False)
                    
                    st.success("Real TESS light curve saved!")
                    
                    lc_results.append({
                        "source_id": source_id,
                        "N Points": len(lc_clean.flux),
                        "Time Span (days)": round(lc_clean.time.value[-1] - lc_clean.time.value[0], 1),
                        "Status": "REAL TESS DATA"
                    })
                    
                else:
                    st.warning("No light curves in MAST archive for this target.")
                    lc_results.append({
                        "source_id": source_id,
                        "N Points": 0,
                        "Time Span (days)": 0,
                        "Status": "NOT IN MAST"
                    })
                    
            except Exception as e:
                st.error(f"Download failed: {e}")
                lc_results.append({
                    "source_id": source_id,
                    "N Points": 0,
                    "Time Span (days)": 0,
                    "Status": "FAILED"
                })
            
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
