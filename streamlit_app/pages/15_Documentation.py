"""
ExoX - Mod15: Documentation & Help
"""

import streamlit as st

st.set_page_config(page_title="Documentation - ExoX", layout="wide")

st.title("Documentation & Help")

tab_intro, tab_stages, tab_faq, tab_cite = st.tabs(
    ["Overview", "Pipeline Stages", "FAQ", "How to Cite"]
)

with tab_intro:
    st.markdown("""
    ## ExoX: Exoplanet Index for K-Dwarf Stars
    
    ExoX helps astronomers search for exoplanets around K-dwarf stars.
    
    ### What is a K-Dwarf?
    K-dwarfs are orange main-sequence stars with temperatures between 3,900-5,300 K.
    They are excellent targets because they are numerous, long-lived, and have
    close-in habitable zones.
    
    ### Pipeline Overview
    1. **Stage 1: K-Dwarf Search** — Validate your target is a genuine K-dwarf
    2. **Stage 2: Exoplanet Probe** — Detect transiting planets using TESS data
    3. **Stage 3: Habitability Grading** — Assess if planets could support liquid water
    4. **Stage 4: Community Sharing** — Export and share your discoveries
    """)

with tab_stages:
    st.markdown("""
    ## Pipeline Stages
    
    ### Stage 1: K-Dwarf Search
    - **Gaia DR3**: Teff, logg, parallax, RUWE
    - **TESS**: Contamination, radius consistency
    - **SIMBAD**: Spectral type, binarity, variability
    - **2MASS**: J-Ks color confirmation
    - **Additional**: WISE, APASS, UCAC4
    
    ### Stage 2: Exoplanet Probe
    - **FITS Images**: Visual confirmation
    - **Light Curves**: TESS photometry
    - **Transit Detection**: BLS periodogram
    
    ### Stage 3: Habitability Grading
    - 7-parameter analysis (HZ, ESI, T_eq, S_eff, eccentricity, tidal lock, HZD)
    
    ### Stage 4: Community Sharing
    - Final report, export, gallery uploads
    """)

with tab_faq:
    st.markdown("""
    ## FAQ
    
    **Q: Why Gaia DR3 as the primary input?**
    Gaia provides the most precise stellar parameters for K-dwarfs.
    
    **Q: What do the HZ Grades mean?**
    A+ (excellent) to F (not habitable). Based on 7-parameter analysis.
    
    **Q: Is the simulated data scientifically valid?**
    No. The demo uses simulated data. Real discoveries require actual photometry.
    """)

with tab_cite:
    st.markdown("""
    ## How to Cite
    
    If you use ExoX in your research:
    
    Balatan, S. C. (2026). ExoX: Exoplanet Index for K-Dwarf Stars.
    https://github.com/sidbalatan/Exoplanet-Index
    """)

st.markdown("---")
st.page_link("Home.py", label="BACK TO HOME")