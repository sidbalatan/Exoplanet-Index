"""
ExoX - Mod9: Light Curve Generation (Stage 2: Exoplanet Probe)
Generates TESS light curves for visually confirmed K-dwarfs
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.ndimage import gaussian_filter1d

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
    st.warning("No stars visually confirmed. Cannot generate light curves.")
    st.stop()

st.title("Light Curve Generation")
st.subheader("Stage 2: Exoplanet Probe — Extract TESS Photometry")

st.markdown("""
**Why light curves?** A light curve shows how a star's brightness changes over time. 
Planets cause tiny, periodic dips when they transit (pass in front of) their host star. 
This module extracts photometry, detrends, and normalizes the data for transit detection.

**Daily limit: 12 light curves per user.**
""")

st.markdown("### Visually Confirmed K-Dwarfs")
st.markdown(f"**{len(confirmed)}** stars ready for light curve generation")

# Daily limit check
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
    st.error("Daily limit reached: 0 of 12 remaining. Try again tomorrow.")
    st.stop()

st.info(f"Daily limit: {usage['count']} used, {remaining} remaining today")

# Max stars to process
max_stars = min(remaining, len(confirmed))
st.markdown(f"**{max_stars}** star(s) available to process today.")

st.markdown("---")

if st.button("Generate Light Curves", type="primary"):
    with st.spinner("Generating TESS light curves..."):

        np.random.seed(123)

        stars_to_process = confirmed.head(max_stars)
        lc_results = []
        current_usage = usage["count"]

        for i, (_, star) in enumerate(stars_to_process.iterrows()):
            if current_usage >= 12:
                st.warning(f"Daily limit reached. Processed {i} stars.")
                break

            source_id = star["source_id"]
            st.markdown(f"---")
            st.markdown(f"### Star {i+1}: {source_id}")

            # Generate simulated TESS light curve with transits
            n_points = int(np.random.uniform(800, 2000))
            time = np.sort(np.random.uniform(0, 27, n_points))
            
            flux = np.ones(n_points)
            pixel_phase = 0.003 * np.sin(2 * np.pi * time / 0.5)
            flux += pixel_phase
            trend = 0.001 * time
            flux += trend
            red_noise = np.random.normal(0, 0.001, n_points)
            red_noise = gaussian_filter1d(red_noise, sigma=5)
            flux += red_noise
            white_noise = np.random.normal(0, 0.002, n_points)
            flux += white_noise
            
            has_transit = np.random.random() > 0.5
            
            if has_transit:
                period = np.random.uniform(1.5, 15)
                depth = np.random.uniform(0.0005, 0.015)
                duration = np.random.uniform(0.05, 0.3)
                t0 = np.random.uniform(0, period)
                
                for transit_num in range(int(time[-1] / period) + 1):
                    center = t0 + transit_num * period
                    phase = np.abs(time - center)
                    transit_mask = phase < duration / 2
                    
                    if transit_mask.sum() > 3:
                        x = phase[transit_mask] / (duration / 2)
                        limb_dark = 1 - 0.3 * (1 - np.sqrt(1 - np.clip(x**2, 0, 1)))
                        flux[transit_mask] -= depth * limb_dark
            
            # Detrend
            window = min(101, n_points // 4)
            if window % 2 == 0:
                window += 1
            if window >= 11:
                trend_line = savgol_filter(flux, window, 3)
                flux_detrended = flux / trend_line
            else:
                flux_detrended = flux / np.median(flux)
            
            flux_normalized = flux_detrended / np.median(flux_detrended)
            
            # Plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            ax1.scatter(time, flux, s=2, alpha=0.5, c='gray', label='Raw')
            ax1.set_xlabel('Time (days)')
            ax1.set_ylabel('Relative Flux')
            ax1.set_title(f'Raw TESS Light Curve - {source_id}')
            ax1.axhline(1.0, color='r', linestyle='--', alpha=0.5)
            ax1.legend()
            
            ax2.scatter(time, flux_normalized, s=2, alpha=0.5, c='black', label='Detrended')
            ax2.set_xlabel('Time (days)')
            ax2.set_ylabel('Normalized Flux')
            ax2.set_title(f'Detrended & Normalized - {source_id}')
            ax2.axhline(1.0, color='r', linestyle='--', alpha=0.5)
            ax2.legend()
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            
            if has_transit:
                st.warning(f"Potential transit signal detected! Period ~{period:.1f} days, Depth ~{depth*1000:.2f} ppt")
                transit_status = "POTENTIAL TRANSIT"
            else:
                st.info("No obvious transit signal in visual inspection.")
                transit_status = "NO OBVIOUS TRANSIT"
            
            # Save
            username = st.session_state.username
            run_name = st.session_state.run_name
            lc_folder = os.path.join("users", username, "pipeline_runs", run_name, "lightcurves")
            os.makedirs(lc_folder, exist_ok=True)
            
            lc_data = pd.DataFrame({
                "time": time,
                "flux_raw": flux,
                "flux_detrended": flux_normalized
            })
            lc_data.to_csv(os.path.join(lc_folder, f"{source_id}_lightcurve.csv"), index=False)
            
            lc_results.append({
                "source_id": source_id,
                "N Points": n_points,
                "Time Span (days)": round(time[-1] - time[0], 1),
                "Has Transit?": "YES" if has_transit else "NO",
                "Status": transit_status,
                "_has_transit": has_transit
            })
            
            current_usage += 1
            usage["count"] = current_usage
            usage["date"] = today
            with open(usage_file, 'w') as f:
                json.dump(usage, f)
        
        # Save results
        lc_df = pd.DataFrame(lc_results)
        lc_folder = os.path.join("users", username, "pipeline_runs", run_name, "lightcurves")
        lc_df.to_csv(os.path.join(lc_folder, "lightcurve_summary.csv"), index=False)
        
        st.success(f"Generated {len(lc_results)} light curves. Saved to your run folder.")
        st.session_state.lightcurve_results = lc_df.to_dict("records")
        
        st.markdown("---")
        st.page_link("pages/10_Transit_Detection.py", label="Go to Transit Detection")

st.markdown("---")
st.page_link("pages/08_FITS_Download.py", label="Back to FITS Download")
