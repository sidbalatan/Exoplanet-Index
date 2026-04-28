"""
ExoX - Mod2: Target Input
Two methods: Manual input or CSV upload
"""

import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

st.set_page_config(page_title="Target Input - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

st.title("Target Input")
st.subheader("Enter the stars you want to search")

with st.expander("Why Gaia DR3?", expanded=True):
    st.markdown("""
    **Gaia DR3 is the recommended input** because it provides precise stellar parameters
    essential for K-dwarf classification. You can also use TIC IDs, coordinates, or upload
    a CSV file with your own target list.
    """)

# ============================================
# METHOD SELECTION
# ============================================
st.markdown("### Select Input Method")
input_method = st.radio(
    "Choose method:",
    ["Manual Input (Gaia, TIC, or Coordinates)", "CSV Upload"],
    horizontal=True
)

target_ids = []
coords_list = []

# ============================================
# METHOD 1: MANUAL INPUT
# ============================================
if input_method == "Manual Input (Gaia, TIC, or Coordinates)":
    st.markdown("#### Manual Input")
    
    manual_type = st.selectbox(
        "Input type:",
        ["Gaia DR3 IDs", "TESS TIC IDs", "RA/Dec Coordinates"]
    )
    
    if manual_type == "Gaia DR3 IDs":
        st.caption("One ID per line, or comma-separated. 19-digit numbers.")
        text = st.text_area("Gaia DR3 IDs", placeholder="2272884155435783424\n3308041786825116672", height=150, label_visibility="collapsed", key="gaia_text")
        if text:
            ids = text.replace(",", " ").replace("\n", " ").split()
            target_ids = [id.strip() for id in ids if id.strip().isdigit() and len(id.strip()) >= 18]

    elif manual_type == "TESS TIC IDs":
        st.caption("One ID per line, or comma-separated.")
        text = st.text_area("TIC IDs", placeholder="118809859\n123456789", height=150, label_visibility="collapsed", key="tic_text")
        if text:
            ids = text.replace(",", " ").replace("\n", " ").split()
            target_ids = [f"TIC_{id.strip()}" for id in ids if id.strip().isdigit()]

    else:
        st.caption("One pair per line: RA Dec (in decimal degrees)")
        text = st.text_area("Coordinates", placeholder="185.458 -63.411\n336.103 60.486", height=150, label_visibility="collapsed", key="coord_text")
        if text:
            for line in text.strip().split("\n"):
                parts = line.strip().split()
                if len(parts) == 2:
                    try:
                        ra = float(parts[0])
                        dec = float(parts[1])
                        if 0 <= ra <= 360 and -90 <= dec <= 90:
                            target_ids.append(f"COORD_{ra}_{dec}")
                            coords_list.append({"ra": ra, "dec": dec})
                    except ValueError:
                        pass

# ============================================
# METHOD 2: CSV UPLOAD
# ============================================
else:
    st.markdown("#### Upload CSV File")
    st.caption("CSV must have columns named: ra, dec (in decimal degrees). Optional: objid, Teff.")
    
    uploaded_file = st.file_uploader("Choose CSV", type="csv", key="csv_upload")
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Loaded {len(df)} rows")
            
            # Show preview
            st.dataframe(df.head(), use_container_width=True)
            
            # Check for required columns
            if "ra" in df.columns and "dec" in df.columns:
                # Use RA/Dec as target IDs
                for _, row in df.iterrows():
                    ra = row["ra"]
                    dec = row["dec"]
                    target_ids.append(f"COORD_{ra}_{dec}")
                    coords_list.append({"ra": ra, "dec": dec})
                    
                    # Also keep objid if available
                    if "objid" in df.columns:
                        target_ids[-1] = str(row["objid"])
                
                st.success(f"Found {len(target_ids)} targets with valid coordinates")
                
            elif "source_id" in df.columns or "gaia_id" in df.columns:
                id_col = "source_id" if "source_id" in df.columns else "gaia_id"
                target_ids = [str(id) for id in df[id_col].dropna().tolist()]
                st.success(f"Found {len(target_ids)} Gaia IDs")
                
            else:
                st.error("CSV must have 'ra' and 'dec' columns, or a 'source_id' column.")
                
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

# ============================================
# TARGET SUMMARY
# ============================================
st.markdown("---")
st.markdown("### Target Summary")

if target_ids:
    target_ids = list(dict.fromkeys(target_ids))
    st.success(f"Detected {len(target_ids)} targets")
    
    preview_data = []
    for i, tid in enumerate(target_ids[:10]):
        preview_data.append({"index": i+1, "target_id": str(tid)[:50]})
    st.dataframe(pd.DataFrame(preview_data).set_index("index"), use_container_width=True)
    
    if len(target_ids) > 10:
        st.caption(f"...and {len(target_ids) - 10} more")
else:
    st.info("Enter targets above or upload a CSV file.")

# ============================================
# SAVE
# ============================================
if target_ids:
    user_run_name = st.text_input(
        "Run Name (optional)",
        value=f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        key="run_name_input"
    )
    
    if st.button("SAVE TARGETS & CONTINUE", type="primary", use_container_width=True):
        username = st.session_state.username
        run_folder = os.path.join("users", username, "pipeline_runs", user_run_name)
        os.makedirs(run_folder, exist_ok=True)
        
        # Save targets
        targets_df = pd.DataFrame({"target_id": target_ids})
        if coords_list:
            coords_df = pd.DataFrame(coords_list)
            targets_df = pd.concat([targets_df, coords_df], axis=1)
        targets_df.to_csv(os.path.join(run_folder, "input_targets.csv"), index=False)
        
        # Save run config
        config = {
            "run_name": user_run_name,
            "input_method": input_method,
            "n_targets": len(target_ids),
            "created_at": datetime.now().isoformat(),
            "status": "targets_loaded"
        }
        with open(os.path.join(run_folder, "run_config.json"), "w") as f:
            json.dump(config, f, indent=2)
        
        st.session_state.run_name = user_run_name
        st.session_state.target_ids = target_ids
        st.session_state.n_targets = len(target_ids)
        st.session_state.coords_list = coords_list
        
        st.success(f"Saved {len(target_ids)} targets to run: {user_run_name}")
        st.markdown("")
        st.page_link("pages/03_Gaia_Filter.py", label="GO TO GAIA FILTER")

st.markdown("---")
st.page_link("Home.py", label="BACK TO HOME")
