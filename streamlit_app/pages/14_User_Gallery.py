"""
ExoX - Mod14: User Upload Gallery (Stage 4: Community Sharing)
Upload and share your discoveries with likes and comments
"""

import streamlit as st
import os
import json
from datetime import datetime

st.set_page_config(page_title="User Gallery - ExoX", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login to upload to the gallery.")
    st.page_link("pages/01_Register.py", label="Go to Login")
    st.stop()

st.title("User Upload Gallery")
st.subheader("Stage 4: Community Sharing — Share Your Discoveries")

st.markdown("""
Upload your light curves, transit plots, and habitability analyses to share with 
the ExoX community. Other astronomers can view, like, and comment on your work.

**What to upload:**
- Light curve plots (raw and detrended)
- Phase-folded transit curves
- Habitability analysis results
- Pipeline summary screenshots
""")

# Upload form
st.markdown("---")
st.markdown("### Upload Your Discovery")

with st.form("gallery_upload"):
    title = st.text_input("Title", placeholder="e.g., K3 Dwarf Transit Detection")
    description = st.text_area("Description", placeholder="Describe your discovery...")
    category = st.selectbox("Category", ["Transit", "Light Curve", "Habitability", "FITS Image", "Pipeline", "Other"])
    tags = st.text_input("Tags (comma separated)", placeholder="K-dwarf, TESS, transit")
    
    uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])
    
    submitted = st.form_submit_button("Upload to Gallery", type="primary")
    
    if submitted:
        if uploaded_file and title:
            username = st.session_state.username
            gallery_folder = os.path.join("users", username, "gallery_uploads")
            os.makedirs(gallery_folder, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{username}_{timestamp}.png"
            filepath = os.path.join(gallery_folder, filename)
            
            with open(filepath, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Save metadata
            metadata = {
                "title": title,
                "description": description,
                "category": category,
                "tags": tags,
                "username": username,
                "filename": filename,
                "date": datetime.now().isoformat(),
                "likes": 0,
                "comments": []
            }
            
            meta_file = os.path.join(gallery_folder, f"{username}_{timestamp}.json")
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            st.success("Upload successful! Your image has been submitted to the gallery.")
            st.balloons()
        else:
            st.error("Please provide a title and select an image.")

# Recent uploads
st.markdown("---")
st.markdown("### Recent Community Uploads")

recent_uploads = [
    {"user": "@astro_hunter", "title": "K2V Transit — 8.3 day period", "likes": 12, "comments": 3, "date": "2026-04-20"},
    {"user": "@exoplanet_phd", "title": "Habitable Zone Analysis: Grade A", "likes": 8, "comments": 5, "date": "2026-04-18"},
    {"user": "@kdwarf_fan", "title": "TESS Light Curve with Clear Dip", "likes": 15, "comments": 7, "date": "2026-04-15"},
    {"user": "@citizen_sci", "title": "First Detection: Sub-Neptune Candidate", "likes": 20, "comments": 9, "date": "2026-04-12"},
]

for item in recent_uploads:
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{item['title']}**")
            st.caption(f"by {item['user']} | {item['date']}")
        with col2:
            st.markdown(f"Likes: {item['likes']}")
        with col3:
            st.markdown(f"Comments: {item['comments']}")

st.markdown("---")
st.page_link("pages/13_Editor_Gallery.py", label="GO TO EDITOR'S GALLERY")
st.page_link("Home.py", label="BACK TO HOME")
