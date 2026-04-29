"""
Shared progress tracker for all ExoX modules
"""

import streamlit as st

def show_progress(current_stage, current_module):
    """
    Display a progress bar showing pipeline stages.
    
    Args:
        current_stage: Integer 1-4
        current_module: String module name
    """
    stages = [
        {"num": 1, "name": "K-Dwarf Search", "modules": "Gaia, TESS, SIMBAD"},
        {"num": 2, "name": "Exoplanet Probe", "modules": "FITS, Light Curves, BLS"},
        {"num": 3, "name": "Characterization", "modules": "2MASS, WISE, Archive, Habitability"},
        {"num": 4, "name": "Community", "modules": "Report, Gallery"},
    ]
    
    st.markdown("---")
    st.markdown("### Pipeline Progress")
    
    # Progress bar
    progress = current_stage / 4
    st.progress(progress, text=f"Stage {current_stage} of 4: {stages[current_stage-1]['name']}")
    
    # Stage indicators
    cols = st.columns(4)
    for i, stage in enumerate(stages):
        with cols[i]:
            if i + 1 < current_stage:
                st.success(f"Stage {i+1}")
            elif i + 1 == current_stage:
                st.info(f"Stage {i+1} (Current)")
            else:
                st.markdown(f"Stage {i+1}")
            st.caption(stage["name"])
    
    st.markdown(f"**Current Module:** {current_module}")
    st.markdown("---")

# Usage in any module:
# from components.progress_bar import show_progress
# show_progress(1, "Gaia DR3 Filter")
