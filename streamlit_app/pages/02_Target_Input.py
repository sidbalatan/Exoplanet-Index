"""
ExoX - Mod2: Target Input
Input Gaia DR3 IDs, TIC IDs, or coordinates
"""

import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Target Input - ExoX",
    page_icon=":dart:",
    layout="wide"
)

# ============================================
# CHECK LOGIN
# ============================================
if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

# ============================================
# HEADER
# ============================================
st.title("Target Input")
st.subheader("Enter the stars you want to search")

# ============================================
# EXPLANATION
# ============================================
with st.expander("Why Gaia DR3?", expanded=True):
    st.markdown("""
    **Gaia DR3 is the recommended input** because it provides:
    
    - **Parallax** — accurate distance measurement
    - **Teff, logg, [Fe/H]** — essential for K-dwarf classification
    - **RUWE** — flags binary stars and astrometric issues
    - **G, BP, RP magnitudes** — photometry for HR diagram placement
    
    You can also use TESS TIC IDs or RA/Dec coordinates as alternatives.
    """)

# ============================================
# INPUT METHOD SELECTION
# ============================================
st.markdown("### Select Input Method")

input_method = st.radio(
    "Choose how to input your targets:",
    ["Gaia DR3 IDs", "TESS TIC IDs", "RA/Dec Coordinates", "CSV Upload"],
    horizontal=True
)

target_ids = []

# ============================================
# GAIA DR3 INPUT
# ============================================
if input_method == "Gaia DR3 IDs":
    st.markdown("#### Enter Gaia DR3 Source IDs")
    st.caption("One ID per line, or comma-separated")

    gaia_text = st.text_area(
        "Gaia DR3 IDs",
        placeholder="1234567890123456789\n9876543210987654321",
        height=150,
        label_visibility="collapsed",
        key="gaia_input"
    )

    if gaia_text:
        ids = gaia_text.replace(",", " ").replace("\n", " ").split()
        target_ids = [id.strip() for id in ids if id.strip().isdigit() and len(id.strip()) >= 18]

# ============================================
# TESS TIC INPUT
# ============================================
elif input_method == "TESS TIC IDs":
    st.markdown("#### Enter TESS TIC IDs")
    st.caption("One ID per line, or comma-separated")

    tic_text = st.text_area(
        "TIC IDs",
        placeholder="118809859\n123456789",
        height=150,
        label_visibility="collapsed",
        key="tic_input"
    )

    if tic_text:
        ids = tic_text.replace(",", " ").replace("\n", " ").split()
        target_ids = [f"TIC_{id.strip()}" for id in ids if id.strip().isdigit()]

# ============================================
# RA/DEC INPUT
# ============================================
elif input_method == "RA/Dec Coordinates":
    st.markdown("#### Enter Coordinates")
    st.caption("One pair per line: RA Dec (in decimal degrees)")

    coord_text = st.text_area(
        "Coordinates",
        placeholder="231.9278 2.5977\n82.7072 -67.0986",
        height=150,
        label_visibility="collapsed",
        key="coord_input"
    )

    if coord_text:
        lines = coord_text.strip().split("\n")
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    ra = float(parts[0])
                    dec = float(parts[1])
                    if 0 <= ra <= 360 and -90 <= dec <= 90:
                        target_ids.append(f"COORD_{ra}_{dec}")
                except ValueError:
                    pass

# ============================================
# CSV UPLOAD
# ============================================
else:
    st.markdown("#### Upload CSV File")
    st.caption("CSV must have a column named: source_id, gaia_id, tic_id, ra, or dec")

    uploaded_file = st.file_uploader("Choose CSV", type="csv", key="csv_upload")

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Loaded {len(df)} rows")
            st.dataframe(df.head(), use_container_width=True)

            for col in ["source_id", "gaia_id", "tic_id", "id"]:
                if col in df.columns:
                    target_ids = [str(id) for id in df[col].dropna().tolist()]
                    break

            if not target_ids and "ra" in df.columns and "dec" in df.columns:
                for _, row in df.iterrows():
                    target_ids.append(f"COORD_{row['ra']}_{row['dec']}")

        except Exception as e:
            st.error(f"Error reading CSV: {e}")

# ============================================
# ALWAYS SHOW SAVE SECTION
# ============================================
st.markdown("---")
st.markdown("### Pipeline Settings")

# Show detected targets
if target_ids:
    target_ids = list(dict.fromkeys(target_ids))
    st.success(f"Detected {len(target_ids)} targets")
    st.dataframe(
        pd.DataFrame({"target_id": target_ids, "index": range(1, len(target_ids)+1)}).set_index("index"),
        use_container_width=True
    )
else:
    st.info("Enter target IDs above or upload a CSV file.")

# Run name - different key to avoid conflict
user_run_name = st.text_input(
    "Run Name (optional)",
    value=f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    key="user_run_name"
)

# Save button
if st.button("Save Targets & Continue", type="primary", use_container_width=True):
    if not target_ids:
        st.error("Please enter at least one valid target ID.")
    else:
        username = st.session_state.username
        run_folder = os.path.join("users", username, "pipeline_runs", user_run_name)
        os.makedirs(run_folder, exist_ok=True)

        targets_df = pd.DataFrame({"target_id": target_ids})
        targets_df.to_csv(os.path.join(run_folder, "input_targets.csv"), index=False)

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

        st.success(f"Saved {len(target_ids)} targets to run: {user_run_name}")

        if st.button("Go to Gaia Filter"):
            st.switch_page("pages/03_Gaia_Filter.py")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.caption("Targets will be saved to your personal workspace and processed through the pipeline.")
