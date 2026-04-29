"""
ExoX - K-Dwarf Certification Report
Presented after Stage 1 completion
"""

import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

st.set_page_config(page_title="K-Dwarf Certificate - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

if "simbad_results" not in st.session_state:
    st.warning("Complete SIMBAD first.")
    st.stop()

simbad_df = pd.DataFrame(st.session_state.simbad_results)
certified = simbad_df[simbad_df["_passed"] == True] if "_passed" in simbad_df.columns else simbad_df

st.markdown("---")
st.markdown("<h1 style='text-align: center; color: #28a745;'>STAGE 1 COMPLETE</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>K-Dwarf Discovery Certified</h2>", unsafe_allow_html=True)

st.markdown("---")

# Congratulations banner
st.success(f"""
### Congratulations, {st.session_state.username}!

You have successfully completed the **K-Dwarf Search** — the first major milestone 
in exoplanet discovery. Your rigorous analysis across three major astronomical 
catalogs has identified **{len(certified)} certified K-dwarf star(s)** ready for 
exoplanet investigation.
""")

# Summary metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Input Stars", st.session_state.get("n_targets", "N/A"))
with col2:
    st.metric("Gaia Survivors", st.session_state.get("n_survivors", "N/A"))
with col3:
    n_tess = st.session_state.get("n_tess_passed", "N/A")
    st.metric("TESS Matched", n_tess if n_tess is not None else "N/A")
with col4:
    st.metric("K-Dwarfs Certified", len(certified))

st.markdown("---")

# Pipeline funnel
st.markdown("### Your Analysis Pipeline")
st.markdown(f"""
| Stage | Catalog | Purpose | Result |
|-------|---------|---------|--------|
| 1 | **Gaia DR3** | Temperature, surface gravity, parallax, RUWE | Stars validated |
| 2 | **TESS/TIC** | Contamination check, TESS observability | Stars matched |
| 3 | **SIMBAD** | Literature spectral type verification | K-dwarfs confirmed |
""")

st.markdown("---")

# Certified K-Dwarfs table
st.markdown("### Certified K-Dwarf Stars")

if len(certified) > 0:
    display_cols = ["source_id", "SIMBAD ID", "Spectral Type", "Object Type", "Status"]
    available = [c for c in display_cols if c in certified.columns]
    st.dataframe(certified[available], use_container_width=True)
    
    # Download certificate
    report_text = f"""
    EXOX K-DWARF CERTIFICATION REPORT
    {'='*50}
    Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    Researcher: {st.session_state.username}
    
    PIPELINE SUMMARY:
    Input Stars: {st.session_state.get('n_targets', 'N/A')}
    Gaia Survivors: {st.session_state.get('n_survivors', 'N/A')}
    TESS Matched: {n_tess}
    K-Dwarfs Certified: {len(certified)}
    
    CATALOGS QUERIED:
    - Gaia DR3 (ESA)
    - TESS Input Catalog (NASA)
    - SIMBAD (CDS Strasbourg)
    
    CERTIFIED STARS:
    """
    for _, star in certified.iterrows():
        report_text += f"\n  {star.get('source_id', 'N/A')} - {star.get('Spectral Type', 'N/A')}"
    
    st.download_button(
        "DOWNLOAD CERTIFICATE (TXT)",
        report_text,
        f"k_dwarf_certificate_{datetime.now().strftime('%Y%m%d')}.txt",
        "text/plain",
        use_container_width=True
    )
else:
    st.info("No K-dwarfs certified in this run.")

st.markdown("---")

# What this means
st.markdown("### What This Means")
st.markdown(f"""
Your **{len(certified)} certified K-dwarf(s)** have passed rigorous validation:

- **Temperature** between 3,900-5,300 K (orange dwarf range)
- **Surface gravity** consistent with main sequence stars
- **Parallax measurements** reliable enough for distance calculation
- **No binarity flags** that would complicate exoplanet detection
- **Low contamination** in TESS data for clean transit signals

These stars are now ready for **Stage 2: Exoplanet Probe**, where you will 
search for transiting planets using real TESS photometry.
""")

st.markdown("---")

# Next step
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Ready for Exoplanet Detection?")
    st.page_link("pages/06_FITS_Download.py", label="START STAGE 2: EXOPLANET PROBE")
with col2:
    st.markdown("### Review Your Data")
    st.page_link("pages/05_SIMBAD_CrossMatch.py", label="BACK TO SIMBAD RESULTS")

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>"
    "ExoX v0.1 | K-Dwarf Search Complete | Data sourced from ESA Gaia, NASA TESS, CDS SIMBAD"
    "</p>",
    unsafe_allow_html=True
)
