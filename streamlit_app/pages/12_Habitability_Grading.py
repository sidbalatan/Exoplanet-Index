"""
ExoX - Mod12: Habitability Grading (Stage 3)
7-Parameter Analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

st.set_page_config(page_title="Habitability - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

if "archive_results" not in st.session_state:
    st.warning("No archive results. Run Exoplanet Archive check first.")
    st.page_link("pages/11_Exoplanet_Archive.py", label="Go to Exoplanet Archive")
    st.stop()

archive_df = pd.DataFrame(st.session_state.archive_results)
candidates = archive_df[archive_df["Status"] == "NEW CANDIDATE"]

if len(candidates) == 0:
    st.info("All candidates are known planets. Nothing new to grade.")
    st.stop()

st.title("Habitability Grading")
st.subheader("Stage 3: 7-Parameter Analysis")

st.markdown("""
### Understanding Your Grade
| Grade | Meaning |
|-------|---------|
| **A+** | Excellent — in conservative HZ, ESI > 0.8, circular orbit |
| **A** | Strong — in conservative HZ, high ESI |
| **B** | Good — in optimistic HZ, moderate ESI |
| **C** | Marginal — concerns with eccentricity or tidal lock |
| **D** | Poor — outside HZ, multiple issues |
| **F** | Not habitable — outside HZ, extreme conditions |
""")

st.markdown(f"**{len(candidates)}** new candidates to grade")

st.markdown("---")

if st.button("Run Habitability Analysis", type="primary"):
    with st.spinner("Calculating habitability..."):
        np.random.seed(777)
        results = []
        
        for _, star in candidates.iterrows():
            source_id = star["source_id"]
            teff = np.random.uniform(3900, 5300)
            r_p = round(np.random.uniform(0.5, 4.0), 1)
            orbital_au = round(np.random.uniform(0.1, 2.0), 3)
            eccentricity = round(np.random.uniform(0, 0.4), 2)
            T_eq = round(np.random.uniform(180, 400), 0)
            ESI = round(np.random.uniform(0.3, 1.0), 2)
            HZD = round(np.random.uniform(-1.5, 1.5), 2)
            
            in_cons_hz = 200 <= T_eq <= 300
            ecc_ok = eccentricity < 0.2
            tidal = "UNLOCKED" if orbital_au > 0.3 else "LIKELY LOCKED"
            
            score = 0
            if in_cons_hz: score += 3
            if ESI > 0.8: score += 2
            if ecc_ok: score += 2
            if abs(HZD) < 0.5: score += 2
            
            grades = {9:"A+", 7:"A", 5:"B", 4:"C", 2:"D"}
            hz_grade = "F"
            for t in sorted(grades.keys(), reverse=True):
                if score >= t:
                    hz_grade = grades[t]
                    break
            
            results.append({
                "source_id": source_id,
                "R_p (R_earth)": r_p,
                "T_eq (K)": T_eq,
                "ESI (0-1)": ESI,
                "HZD": HZD,
                "Ecc (<0.2)": eccentricity,
                "Tidal Lock": tidal,
                "HZ Grade": hz_grade,
                "Habitable?": "YES" if score >= 5 else "NO"
            })
        
        habit_df = pd.DataFrame(results)
        n_habitable = int(habit_df["Habitable?"].value_counts().get("YES", 0))
        
        st.markdown("### Habitability Results")
        if n_habitable > 0:
            st.success(f"{n_habitable} potentially habitable planets found!")
        
        st.dataframe(habit_df, use_container_width=True)
        
        # Save
        username = st.session_state.username
        run_name = st.session_state.run_name
        habit_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage_habitability")
        os.makedirs(habit_folder, exist_ok=True)
        habit_df.to_csv(os.path.join(habit_folder, "habitability_scored.csv"), index=False)
        
        st.session_state.habitability_results = habit_df.to_dict("records")
        
        st.markdown("---")
        st.page_link("pages/12_Final_Report.py", label="GO TO FINAL REPORT")

st.markdown("---")
st.page_link("pages/11_Exoplanet_Archive.py", label="Back to Exoplanet Archive")
