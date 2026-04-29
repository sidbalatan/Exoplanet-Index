"""
Session Manager - Save and restore pipeline progress
"""

import streamlit as st
import json
import os
from datetime import datetime

def save_progress():
    """Save current pipeline state to user folder."""
    if not st.session_state.get("logged_in"):
        return False
    
    username = st.session_state.username
    save_file = f"users/{username}/pipeline_state.json"
    os.makedirs(f"users/{username}", exist_ok=True)
    
    # Collect all important session state
    state = {}
    for key in [
        "logged_in", "username", "run_name", "target_ids", "n_targets",
        "gaia_survivors", "n_survivors", "certified_k_dwarfs",
        "tess_results", "n_tess_passed",
        "simbad_results", "n_simbad_passed",
        "processed_fits", "processed_lc",
        "planet_candidates", "n_planet_candidates",
        "current_module"
    ]:
        if key in st.session_state:
            val = st.session_state[key]
            # Convert DataFrames to dicts
            if hasattr(val, 'to_dict'):
                val = val.to_dict('records') if hasattr(val, 'to_dict') else str(val)
            state[key] = val
    
    state["saved_at"] = datetime.now().isoformat()
    
    with open(save_file, 'w') as f:
        json.dump(state, f, indent=2, default=str)
    
    return True

def load_progress():
    """Load saved pipeline state."""
    if not st.session_state.get("logged_in"):
        return False
    
    username = st.session_state.username
    save_file = f"users/{username}/pipeline_state.json"
    
    if not os.path.exists(save_file):
        return False
    
    with open(save_file, 'r') as f:
        state = json.load(f)
    
    # Restore session state
    for key, value in state.items():
        if key not in ["saved_at", "logged_in", "username"]:
            st.session_state[key] = value
    
    return True

def get_saved_module():
    """Get the last module the user was on."""
    if not st.session_state.get("logged_in"):
        return None
    
    username = st.session_state.username
    save_file = f"users/{username}/pipeline_state.json"
    
    if not os.path.exists(save_file):
        return None
    
    with open(save_file, 'r') as f:
        state = json.load(f)
    
    return state.get("current_module")

def show_save_button(current_module_name):
    """Display save/load buttons in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Save Progress")
    
    if st.sidebar.button("Save Current State", use_container_width=True):
        st.session_state.current_module = current_module_name
        if save_progress():
            st.sidebar.success("Progress saved!")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Navigation")
    
    # Show links to modules based on saved state
    if st.session_state.get("certified_k_dwarfs"):
        st.sidebar.page_link("pages/06_FITS_Download.py", label="FITS Images")
        st.sidebar.page_link("pages/07_LightCurve_Generation.py", label="Light Curves")
    
    if st.session_state.get("planet_candidates"):
        st.sidebar.page_link("pages/08_Transit_Detection.py", label="Transit Detection")
