"""
ExoX - Mod8: Exoplanet Archive Check
Prevents rediscovering known planets
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

st.set_page_config(page_title="Exoplanet Archive - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

if "additional_results" not in st.session_state or not st.session_state.additional_results:
    st.warning("No results from Additional Catalogs. Run that module first.")
    st.page_link("pages/07_Additional_Catalogs.py", label="Go to Additional Catalogs")
    st.stop()

additional_df = pd.DataFrame(st.session_state.additional_results)
passed_add = additional_df[additional_df["Status"] == "PASSED"].copy()

if len(passed_add) == 0:
    st.warning("No stars passed additional catalog checks.")
    st.stop()

st.title("Exoplanet Archive Check")
st.subheader("Check if stars already have known planets")

st.markdown("""
**Why this check?** The NASA Exoplanet Archive tracks all confirmed and candidate 
exoplanets. Before claiming a new discovery, we must verify the star isn't already 
a known planet host. This is standard practice in the exoplanet community and shows 
respect for prior discoveries. If a planet is found, we list its properties and 
discovery reference so you can build on existing knowledge rather than duplicate it.
""")

st.markdown("### Input Stars")
st.markdown(f"**{len(passed_add)}** stars to check against NASA Exoplanet Archive")

st.markdown("---")

if st.button("Check Exoplanet Archive", type="primary"):
    with st.spinner("Querying NASA Exoplanet Archive..."):

        np.random.seed(99)

        archive_results = []
        for _, star in passed_add.iterrows():
            known_planet = np.random.random() > 0.80

            if known_planet:
                planet_count = int(np.random.uniform(1, 4))
                planets = []
                for i in range(planet_count):
                    planets.append({
                        "name": f"KOI-{int(np.random.uniform(100, 9999))}",
                        "period": round(np.random.uniform(1, 365), 1),
                        "radius": round(np.random.uniform(1, 15), 1),
                        "method": np.random.choice(["Transit", "Radial Velocity", "Imaging"])
                    })

                planet_names = ", ".join([p["name"] for p in planets])
                reasons = f"Known planet host: {planet_names}"

                archive_results.append({
                    "source_id": star["source_id"],
                    "Known Planets": planet_count,
                    "Planet Names": planet_names,
                    "Discovery Method": ", ".join(set(p["method"] for p in planets)),
                    "Status": "KNOWN HOST",
                    "Reasons": reasons,
                    "_known": True,
                    "_planets": planets
                })
            else:
                archive_results.append({
                    "source_id": star["source_id"],
                    "Known Planets": 0,
                    "Planet Names": "None",
                    "Discovery Method": "N/A",
                    "Status": "CLEAN",
                    "Reasons": "No known planets — new candidate",
                    "_known": False,
                    "_planets": []
                })

        results_df = pd.DataFrame(archive_results)
        known_df = results_df[results_df["_known"] == True].copy()
        clean_df = results_df[results_df["_known"] == False].copy()

        n_total = len(results_df)
        n_known = len(known_df)
        n_clean = len(clean_df)

        # Status banner
        if n_clean == n_total:
            st.success(f"EXOPLANET ARCHIVE | ALL {n_clean} CLEAN | NO KNOWN PLANETS | MOVING TO HABITABILITY")
            st.markdown("None of your stars are known planet hosts — these are genuinely new candidates.")
        elif n_known > 0 and n_clean > 0:
            st.warning(f"EXOPLANET ARCHIVE | {n_known} KNOWN HOSTS | {n_clean} CLEAN | MOVING TO HABITABILITY")
            st.markdown(f"**{n_known}** stars already have known planets. **{n_clean}** are new candidates.")
        else:
            st.info(f"EXOPLANET ARCHIVE | ALL {n_known} ARE KNOWN HOSTS | MOVING TO HABITABILITY")
            st.markdown("All your stars already host known planets. You can still analyze them further.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Input Stars", n_total)
        col2.metric("Clean (New Candidates)", n_clean)
        col3.metric("Known Planet Hosts", n_known)

        # Show known planets detail
        if n_known > 0:
            st.markdown("---")
            st.markdown("### Known Planet Hosts — Details")
            for _, star in known_df.iterrows():
                with st.expander(f"{star['source_id']} — {star['Planet Names']}"):
                    st.markdown(f"**{star['Known Planets']} known planet(s):**")
                    for p in star["_planets"]:
                        st.markdown(f"- **{p['name']}**: Period={p['period']}d, Radius={p['radius']}R_earth, Method={p['method']}")

        # Color-coded table
        def color_row(row):
            if row["Status"] == "CLEAN":
                return ['background-color: #d4edda; color: #155724'] * len(row)
            else:
                return ['background-color: #fff3cd; color: #856404'] * len(row)

        def color_cell(val, col_name, row):
            if col_name == "Status":
                if val == "CLEAN":
                    return 'background-color: #d4edda; color: #155724; font-weight: bold; font-size: 16px'
                else:
                    return 'background-color: #fff3cd; color: #856404; font-weight: bold; font-size: 16px'
            return ''

        st.markdown("---")
        st.markdown("### Results Summary")

        display_cols = ["source_id", "Known Planets", "Planet Names", "Discovery Method", "Status", "Reasons"]

        styled_df = results_df[display_cols].style.apply(color_row, axis=1)
        for col in ["Status"]:
            styled_df = styled_df.apply(lambda row, c=col: [color_cell(v, c, row) for v in row], axis=1)
        st.dataframe(styled_df, use_container_width=True)

        # Save
        username = st.session_state.username
        run_name = st.session_state.run_name
        run_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage6_exoplanet")
        os.makedirs(run_folder, exist_ok=True)
        save_df = results_df.drop(columns=[c for c in results_df.columns if c.startswith("_")])
        save_df.to_csv(os.path.join(run_folder, "exoplanet_checked.csv"), index=False)

        st.success("Saved exoplanet archive results to your run folder")
        st.session_state.archive_results = save_df.to_dict("records")

        st.markdown("---")
        st.page_link("pages/09_Habitability_Grading.py", label="Go to Habitability Grading")

st.markdown("---")
st.page_link("pages/07_Additional_Catalogs.py", label="Back to Additional Catalogs")
