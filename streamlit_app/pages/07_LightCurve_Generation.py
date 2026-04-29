"""
ExoX - Mod7: Light Curve Generation (Stage 2)
Real TESS light curves — no daily limit
"""

import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Light Curves - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.switch_page("pages/01_Register.py")

if "certified_k_dwarfs" not in st.session_state:
    st.warning("No certified K-dwarfs. Complete Stage 1 first.")
    st.page_link("pages/05_SIMBAD_CrossMatch.py", label="Go to SIMBAD")
    st.stop()

st.title("Light Curve Generation")
st.subheader("Stage 2: Exoplanet Probe — Real TESS Photometry")

certified = st.session_state.certified_k_dwarfs
st.markdown(f"**{len(certified)}** certified K-dwarfs available")

@st.cache_data
def load_seip():
    try: return pd.read_csv("data/SEIP_data_17k.csv")
    except: return None

seip = load_seip()

if "processed_lc" not in st.session_state:
    st.session_state.processed_lc = []

remaining = [c for c in certified if c not in st.session_state.processed_lc]
processed = [c for c in certified if c in st.session_state.processed_lc]

st.markdown(f"**{len(processed)}** processed | **{len(remaining)}** remaining")
st.markdown("---")

if remaining:
    selected = st.multiselect(
        "Select stars to download:",
        remaining,
        default=remaining[:min(1, len(remaining))],
        max_selections=4
    )
    
    if selected:
        if st.button("DOWNLOAD LIGHT CURVES", type="primary"):
            import lightkurve as lk
            from astropy.coordinates import SkyCoord
            import astropy.units as u
            
            for source_id in selected:
                st.markdown(f"### {str(source_id)[:50]}...")
                
                ra, dec = None, None
                
                # Try stored coordinates first
                coords_dict = st.session_state.get("star_coords", {})
                if source_id in coords_dict:
                    ra = coords_dict[source_id].get("ra")
                    dec = coords_dict[source_id].get("dec")
                
                # Fallback to SEIP lookup
                if (ra is None or dec is None) and seip is not None:
                    match = seip[seip["objid"] == str(source_id)]
                    if len(match) == 0:
                        match = seip[seip["objid"].astype(str).str.contains(str(source_id)[:15], na=False)]
                    if len(match) > 0:
                        ra = float(match.iloc[0]["ra"])
                        dec = float(match.iloc[0]["dec"])
                
                if ra is None:
                    st.error("No coordinates found for this star")
                    continue
                
                with st.spinner(f"Downloading from MAST..."):
                    try:
                        coord = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg))
                        search = lk.search_lightcurve(coord, mission="TESS")
                        
                        if search and len(search) > 0:
                            lc = search[0].download().remove_nans()
                            lc = lc.flatten(101).remove_outliers(5)
                            
                            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
                            ax1.set_title('Raw TESS Light Curve')
                            ax2.set_title('Detrended & Normalized')
                            ax2.axhline(1.0, color='r', linestyle='--')
                            plt.tight_layout()
                            st.pyplot(fig)
                            plt.close()
                            
                            # Save
                            lc_folder = os.path.join("users", st.session_state.username,
                                                    "pipeline_runs", st.session_state.run_name, "lightcurves")
                            os.makedirs(lc_folder, exist_ok=True)
                            pd.DataFrame({
                                "time": lc.time.value,
                                "flux_detrended": lc.flux.value
                            }).to_csv(os.path.join(lc_folder, f"{source_id}_lightcurve.csv"), index=False)
                            
                            st.success(f"Saved! {len(lc.flux)} points")
                        else:
                            st.warning("No TESS light curve for this star")
                    except Exception as e:
                        st.error(f"MAST error: {str(e)[:100]}")
                
                st.session_state.processed_lc.append(source_id)
            
            st.rerun()

if processed:
    st.markdown("---")
    st.success(f"{len(processed)} light curves processed")
    st.page_link("pages/08_Transit_Detection.py", label="GO TO TRANSIT DETECTION")

st.markdown("---")
st.page_link("pages/06_FITS_Download.py", label="Back to FITS Images")
