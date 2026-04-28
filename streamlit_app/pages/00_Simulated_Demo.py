"""
ExoX - Simulated Demo
Full pipeline experience with dummy data — no login required
"""

import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(page_title="Demo - ExoX", layout="wide")

st.title("Simulated Pipeline Demo")
st.subheader("Experience the complete ExoX pipeline with dummy data")

st.info("This demo uses simulated data. No real queries are made. No login required.")

if st.button("Start Demo", type="primary", use_container_width=True):
    
    # Stage 1: K-Dwarf Search
    st.markdown("---")
    st.markdown("## STAGE 1: K-DWARF SEARCH")
    
    progress = st.progress(0)
    
    for i, stage in enumerate(["Gaia DR3 Filter", "TESS Cross-Match", "SIMBAD Cross-Match", "2MASS Cross-Match", "Additional Catalogs"]):
        time.sleep(0.5)
        progress.progress((i + 1) / 5)
        st.success(f"Stage {i+1}/5: {stage} — PASSED")
    
    st.success("ALL 5 STAGES PASSED — CERTIFIED K-DWARF")
    st.markdown("""
    Your simulated star **Gaia DR3 1234567890123456789** has been validated:
    - Teff = 4,750 K (K-dwarf range)
    - logg = 4.5 (main sequence)
    - Parallax SNR = 12.3 (reliable distance)
    - RUWE = 1.05 (not binary)
    - SIMBAD: K2V spectral type confirmed
    - 2MASS: J-Ks = 0.72 (K-dwarf color)
    - WISE: Clean, no IR excess
    """)
    
    # Stage 2: Exoplanet Probe
    st.markdown("---")
    st.markdown("## STAGE 2: EXOPLANET PROBE")
    
    progress2 = st.progress(0)
    
    for i, stage in enumerate(["FITS Image Download", "Light Curve Generation", "Transit Detection"]):
        time.sleep(0.5)
        progress2.progress((i + 1) / 3)
        st.success(f"Stage {i+1}/3: {stage} — COMPLETE")
    
    st.success("PLANET CANDIDATE DETECTED")
    st.markdown("""
    **Transit Detected:**
    - Period: 12.4 days
    - Duration: 3.2 hours
    - Depth: 0.85 ppt
    - SNR: 15.7
    
    **Estimated Planet Radius:** 2.8 R_earth (Sub-Neptune)
    """)
    
    # Stage 3: Habitability Grading
    st.markdown("---")
    st.markdown("## STAGE 3: HABITABILITY GRADING")
    
    time.sleep(1)
    
    st.markdown("""
    ### 7-Parameter Analysis Results
    
    | Parameter | Value | Status |
    |-----------|-------|--------|
    | HZ Position | In Conservative HZ | PASS |
    | T_eq | 268 K (200-300) | PASS |
    | ESI | 0.82 (> 0.8) | PASS |
    | S_eff | 1.2 x Earth | MODERATE |
    | Eccentricity | 0.05 (< 0.2) | PASS |
    | Tidal Lock | UNLOCKED | GOOD |
    | HZD | -0.15 (near center) | EXCELLENT |
    
    ### Final Grade: A
    
    **Classification: Potentially Habitable Sub-Neptune**
    """)
    
    st.success("STAGE 3 COMPLETE — GRADE A")
    
    # Stage 4: Community Sharing
    st.markdown("---")
    st.markdown("## STAGE 4: COMMUNITY SHARING")
    
    st.markdown("""
    Your discovery is ready to share with the astronomy community:
    
    1. **Download Results** — CSV, VOTable, FITS formats
    2. **Upload to Gallery** — Share your light curves and plots
    3. **Cite in Papers** — Use the ExoX citation format
    
    *In the full version, register an account to save and share your results.*
    """)
    
    st.balloons()
    st.success("DEMO COMPLETE — Register to run with real data!")

st.markdown("---")
st.page_link("Home.py", label="Back to Home")
