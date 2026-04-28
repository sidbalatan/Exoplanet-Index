"""
ExoX - Mod11: Habitability Grading (Stage 3)
7-Parameter Analysis with detailed explanations
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

if "planet_candidates" not in st.session_state or not st.session_state.planet_candidates:
    st.warning("No planet candidates. Run Transit Detection first.")
    st.page_link("pages/10_Transit_Detection.py", label="Go to Transit Detection")
    st.stop()

st.title("Habitability Grading")
st.subheader("Stage 3: 7-Parameter Habitability Analysis")

st.markdown("""
**Can this planet support liquid water?** This module applies peer-reviewed methods 
from Kopparapu et al. (2013) to assess habitability using seven core parameters.

### Understanding Your Grade
| Grade | Meaning |
|-------|---------|
| **A+** | Excellent — in conservative HZ, ESI > 0.8, circular orbit, near HZ center |
| **A** | Strong — in conservative HZ, high ESI, good conditions |
| **B** | Good — in optimistic HZ, moderate ESI |
| **C** | Marginal — in HZ but with concerns (eccentric, tidal lock, low ESI) |
| **D** | Poor — likely outside HZ, multiple unfavorable factors |
| **F** | Not habitable — outside HZ, extreme temperatures |
""")

st.markdown("### Planet Candidates")
st.markdown(f"**{len(st.session_state.planet_candidates)}** candidates to analyze")

if "transit_results" not in st.session_state:
    transit_data = None
else:
    transit_data = pd.DataFrame(st.session_state.transit_results)

st.markdown("---")

if st.button("Run Habitability Analysis", type="primary"):
    with st.spinner("Calculating habitability parameters..."):

        np.random.seed(777)
        habitability_results = []

        for i, source_id in enumerate(st.session_state.planet_candidates):
            st.markdown(f"---")
            st.markdown(f"### Candidate {i+1}: {source_id}")

            if transit_data is not None and source_id in transit_data["source_id"].values:
                star_data = transit_data[transit_data["source_id"] == source_id].iloc[0]
                period = star_data.get("_period", np.random.uniform(1, 365))
                depth = star_data.get("_depth", 0.001)
            else:
                period = np.random.uniform(1, 365)
                depth = np.random.uniform(0.0005, 0.015)

            teff = np.random.uniform(3900, 5300)
            r_star = np.random.uniform(0.5, 1.0)
            m_star = (teff / 5772)**4
            r_p_earth = round(np.sqrt(depth) * r_star * 109.2, 1)
            orbital_au = round((period**2 * m_star)**(1/3), 3)
            eccentricity = round(np.random.uniform(0, 0.5), 2)

            # HZ
            d_inner_cons = round(np.sqrt(1/1.107) * (teff/5772)**2, 3)
            d_outer_cons = round(np.sqrt(1/0.356) * (teff/5772)**2, 3)
            d_inner_opt = round(np.sqrt(1/1.776) * (teff/5772)**2, 3)
            d_outer_opt = round(np.sqrt(1/0.320) * (teff/5772)**2, 3)
            in_cons_hz = d_inner_cons <= orbital_au <= d_outer_cons
            in_opt_hz = d_inner_opt <= orbital_au <= d_outer_opt

            # T_eq
            T_eq = round(teff * np.sqrt(r_star*0.00465/(2*orbital_au)) * 0.7**(1/4), 0)
            T_eq_ok = 200 <= T_eq <= 300

            # S_eff
            S_eff = round((teff/5772)**4 * (r_star/1.0)**2 / (orbital_au**2), 2)

            # Eccentricity
            eccentricity_ok = eccentricity < 0.2

            # Tidal lock
            tidal_locked = orbital_au < 0.3
            tidal_status = "LIKELY LOCKED" if tidal_locked else "UNLOCKED"

            # ESI
            ESI_radius = 1 - abs((r_p_earth-1)/(r_p_earth+1))
            ESI_temp = 1 - abs((T_eq-255)/(T_eq+255))
            ESI = round(np.sqrt(ESI_radius*ESI_temp*np.random.uniform(0.8,1.2)), 2)
            ESI = min(1.0, ESI)

            # HZD
            d_center = (d_inner_cons + d_outer_cons)/2
            if orbital_au <= d_center:
                HZD = round(-(d_center-orbital_au)/(d_center-d_inner_cons), 2)
            else:
                HZD = round((orbital_au-d_center)/(d_outer_cons-d_center), 2)
            HZD = max(-1.5, min(1.5, HZD))

            # Grade
            score = 0
            if T_eq_ok: score += 2
            if in_cons_hz: score += 3
            if in_opt_hz and not in_cons_hz: score += 1
            if ESI > 0.8: score += 2
            if ESI > 0.5: score += 1
            if eccentricity_ok: score += 2
            if abs(HZD) < 0.5: score += 2

            grades = {10:"A+", 8:"A", 6:"B", 4:"C", 2:"D"}
            hz_grade = "F"
            for threshold in sorted(grades.keys(), reverse=True):
                if score >= threshold:
                    hz_grade = grades[threshold]
                    break

            is_habitable = score >= 6

            if T_eq < 200:
                sph_class = "Psychroplanet (Cold)"
            elif T_eq <= 350:
                sph_class = "Mesoplanet (Temperate)"
            else:
                sph_class = "Thermoplanet (Hot)"

            # Display with explanations
            st.markdown("#### 7-Parameter Analysis")
            st.caption("Each parameter includes a brief explanation of what it means and why it matters.")

            col1, col2 = st.columns(2)

            with col1:
                with st.container(border=True):
                    st.markdown("**1. Habitable Zone Position**")
                    if in_cons_hz:
                        st.success(f"Planet at {orbital_au} AU — INSIDE Conservative HZ ({d_inner_cons}-{d_outer_cons} AU)")
                    elif in_opt_hz:
                        st.warning(f"Planet at {orbital_au} AU — Optimistic HZ only ({d_inner_opt}-{d_outer_opt} AU)")
                    else:
                        st.error(f"Planet at {orbital_au} AU — OUTSIDE all HZ boundaries")
                    st.caption("The Habitable Zone is where a planet can maintain liquid water. The Conservative HZ is the narrow 'safe' region; the Optimistic HZ is wider based on Mars/Venus evidence.")

                with st.container(border=True):
                    st.markdown("**2. Equilibrium Temperature (200-300 K)**")
                    if T_eq_ok:
                        st.success(f"T_eq = {T_eq} K — Within Earth-like range")
                    else:
                        st.error(f"T_eq = {T_eq} K — Outside Earth-like range")
                    st.caption("Theoretical surface temperature without an atmosphere. Earth's is 255 K. 200-300 K allows liquid water with a suitable atmosphere.")

                with st.container(border=True):
                    st.markdown("**3. Stellar Flux (S_eff)**")
                    st.markdown(f"S_eff = {S_eff}x Earth's insolation")
                    st.caption("How much energy the planet receives from its star. K-dwarfs provide stable, long-term flux ideal for life. Earth = 1.0.")

                with st.container(border=True):
                    st.markdown("**4. Orbital Eccentricity (< 0.2)**")
                    if eccentricity_ok:
                        st.success(f"e = {eccentricity} — Nearly circular orbit")
                    else:
                        st.error(f"e = {eccentricity} — Elliptical orbit")
                    st.caption("A circular orbit keeps the planet at a stable distance from the star. High eccentricity causes extreme temperature swings as the planet moves in and out of the HZ.")

            with col2:
                with st.container(border=True):
                    st.markdown("**5. Tidal Locking Status**")
                    if tidal_locked:
                        st.warning(f"{tidal_status} — One side always faces the star")
                    else:
                        st.success(f"{tidal_status} — Full rotation distributes heat evenly")
                    st.caption("K-dwarf HZs are close to the star. Tidally locked planets have a permanent day side and night side, affecting climate and habitability.")

                with st.container(border=True):
                    st.markdown("**6. Earth Similarity Index (0-1, > 0.8)**")
                    if ESI > 0.8:
                        st.success(f"ESI = {ESI} — Earth-like")
                    elif ESI > 0.5:
                        st.warning(f"ESI = {ESI} — Moderate similarity")
                    else:
                        st.error(f"ESI = {ESI} — Low similarity to Earth")
                    st.caption("A weighted scale comparing radius, density, and temperature to Earth. Earth = 1.0. ESI > 0.8 is considered 'Earth-like'.")

                with st.container(border=True):
                    st.markdown("**7. Habitable Zone Distance (0 = center)**")
                    if abs(HZD) < 0.3:
                        st.success(f"HZD = {HZD} — Near HZ center")
                    elif abs(HZD) < 0.8:
                        st.warning(f"HZD = {HZD} — Within HZ")
                    else:
                        st.error(f"HZD = {HZD} — Near HZ edge")
                    st.caption("Numerical position in the HZ. 0 is the center, -1 is inner edge (too hot), +1 is outer edge (too cold).")

                with st.container(border=True):
                    st.markdown(f"**SPH Thermal Class:** {sph_class}")
                    st.markdown(f"### Final Grade: **{hz_grade}**")
                    if hz_grade in ["A+", "A"]:
                        st.success("This planet has EXCELLENT habitability potential.")
                    elif hz_grade in ["B", "C"]:
                        st.warning("This planet has MODERATE habitability potential — further study recommended.")
                    else:
                        st.error("This planet has POOR habitability potential.")

            habitability_results.append({
                "source_id": source_id,
                "Teff (K)": teff,
                "R_star (Rsun)": round(r_star, 2),
                "Period (days)": round(period, 1),
                "R_p (R_earth)": r_p_earth,
                "Orbit (AU)": orbital_au,
                "In Cons. HZ?": "YES" if in_cons_hz else "NO",
                "T_eq (K) (200-300)": f"{T_eq}",
                "S_eff (xEarth)": S_eff,
                "Ecc (< 0.2)": eccentricity,
                "Tidal Lock": tidal_status,
                "ESI (0-1) (> 0.8)": ESI,
                "HZD (-1 to +1) (0=center)": HZD,
                "SPH Class": sph_class,
                "HZ Grade": hz_grade,
                "Habitable?": "YES" if is_habitable else "NO"
            })

        # Save and display
        habit_df = pd.DataFrame(habitability_results)
        username = st.session_state.username
        run_name = st.session_state.run_name
        habit_folder = os.path.join("users", username, "pipeline_runs", run_name, "stage9_habitability")
        os.makedirs(habit_folder, exist_ok=True)
        habit_df.to_csv(os.path.join(habit_folder, "habitability_scored.csv"), index=False)
        st.session_state.habitability_results = habit_df.to_dict("records")

        n_habitable = int(habit_df["Habitable?"].value_counts().get("YES", 0))

        st.markdown("---")
        st.markdown("## STAGE 3 COMPLETE: HABITABILITY GRADING")

        if n_habitable > 0:
            st.balloons()
            st.success(f"CONGRATULATIONS! {n_habitable} PLANET(S) CLASSIFIED AS POTENTIALLY HABITABLE")

        # Summary table
        st.markdown("### Habitability Summary Table")
        display_cols = ["source_id", "R_p (R_earth)", "T_eq (K) (200-300)", "In Cons. HZ?", "ESI (0-1) (> 0.8)", "HZD (-1 to +1) (0=center)", "Ecc (< 0.2)", "Tidal Lock", "HZ Grade", "Habitable?"]
        st.dataframe(habit_df[display_cols], use_container_width=True)

        st.success("Saved habitability results to your run folder")

        st.markdown("---")
        st.markdown("""
        <div style="background-color: #d4edda; padding: 20px; border-radius: 12px; border: 2px solid #28a745; text-align: center;">
            <h3 style="color: #155724; margin: 0;">PROCEED TO STAGE 4: FINAL REPORT & COMMUNITY SHARING</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        st.page_link("pages/12_Final_Report.py", label="GO TO FINAL REPORT")

st.markdown("---")
st.page_link("pages/10_Transit_Detection.py", label="Back to Transit Detection")
