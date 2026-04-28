"""
ExoX - Mod13: Editor's Choice Gallery (Stage 4: Community Sharing)
Curated scientific images from the ExoX community
"""

import streamlit as st
import os
import json
from datetime import datetime

st.set_page_config(page_title="Editor Gallery - ExoX", layout="wide")

st.title("Editor's Choice Gallery")
st.subheader("Stage 4: Community Sharing — Curated Scientific Highlights")

st.markdown("""
The Editor's Choice Gallery showcases the best light curves, transit detections, 
and habitability analyses produced by the ExoX community. Images are selected by 
our editorial team for their scientific quality and visual clarity.

**Want your work featured?** Complete a pipeline run with real data and submit 
your results through the User Gallery.
""")

# Sample gallery data
gallery_items = [
    {
        "title": "Transit Detection: Sub-Neptune around K2 Dwarf",
        "description": "Clear transit signal with 12.4-day period and 0.85 ppt depth. BLS SNR = 15.7.",
        "category": "Transit",
        "date": "2026-04-15",
        "stars": 5
    },
    {
        "title": "Light Curve: K3V Star with Potential Super-Earth",
        "description": "Detrended TESS light curve showing 3.2-hour transit at 5.6-day period.",
        "category": "Light Curve",
        "date": "2026-04-10",
        "stars": 4
    },
    {
        "title": "Habitable Zone Analysis: Grade A Candidate",
        "description": "Planet in conservative HZ with ESI = 0.82, circular orbit, and T_eq = 268 K.",
        "category": "Habitability",
        "date": "2026-04-08",
        "stars": 5
    },
    {
        "title": "FITS Image: Confirmed K-Dwarf in TESS Sector 42",
        "description": "Clean point spread function with no contamination from nearby sources.",
        "category": "FITS Image",
        "date": "2026-04-05",
        "stars": 3
    },
    {
        "title": "Phase-Folded Transit: Neptune-like Planet",
        "description": "Beautifully folded light curve showing ingress, egress, and flat bottom.",
        "category": "Transit",
        "date": "2026-04-01",
        "stars": 4
    },
    {
        "title": "Pipeline Complete: From Gaia to Habitable Planet",
        "description": "Full pipeline run: 10 stars input, 3 K-dwarfs certified, 1 habitable planet found.",
        "category": "Pipeline",
        "date": "2026-03-28",
        "stars": 5
    }
]

# Filter tabs
tab_all, tab_transit, tab_lc, tab_hz, tab_fits = st.tabs(
    ["All", "Transits", "Light Curves", "Habitability", "FITS Images"]
)

active_tab = "All"

# Display gallery
filtered = gallery_items

st.markdown("---")

# Grid display
cols_per_row = 3
for i in range(0, len(filtered), cols_per_row):
    row_items = filtered[i:i+cols_per_row]
    cols = st.columns(cols_per_row)
    
    for j, item in enumerate(row_items):
        with cols[j]:
            with st.container(border=True):
                st.markdown(f"### {item['title'][:50]}...")
                st.caption(f"Category: {item['category']} | {item['date']}")
                st.markdown(item['description'][:120] + "...")
                st.markdown("**" + "★" * item['stars'] + "**")
                
                if st.button(f"View Details", key=f"gallery_{i}_{j}"):
                    st.info("Full image view coming soon. Images will be uploaded by the community.")

st.markdown("---")
st.markdown("### Submit Your Work")
st.markdown("Complete a pipeline run and upload your results to the User Gallery for a chance to be featured here.")
st.page_link("pages/14_User_Gallery.py", label="GO TO USER GALLERY")
st.page_link("Home.py", label="BACK TO HOME")
