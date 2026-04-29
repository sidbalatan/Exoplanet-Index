"""
Shared styling for all ExoX modules
"""

import streamlit as st

def apply_style():
    """Apply consistent styling across all pages."""
    st.markdown("""
    <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global styles */
        .stApp {
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3, h4 {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }
        
        /* Primary button - GREEN */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #28a745, #20c997) !important;
            color: white !important;
            border: none !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            padding: 12px 28px !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3) !important;
            width: 100% !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #218838, #1aa179) !important;
            box-shadow: 0 6px 20px rgba(40, 167, 69, 0.5) !important;
            transform: translateY(-1px) !important;
        }
        
        /* Secondary button */
        .stButton > button[kind="secondary"] {
            border: 2px solid #6c757d !important;
            color: #6c757d !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
        }
        
        /* Page link styled as prominent green button */
        .stPageLink > a {
            background: #28a745 !important;
            color: white !important;
            font-weight: 700 !important;
            font-size: 18px !important;
            padding: 16px 32px !important;
            border-radius: 10px !important;
            text-decoration: none !important;
            text-align: center !important;
            display: block !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 16px rgba(40, 167, 69, 0.4) !important;
            border: none !important;
        }
        
        .stPageLink > a:hover {
            background: #218838 !important;
            box-shadow: 0 6px 24px rgba(40, 167, 69, 0.6) !important;
            transform: translateY(-2px) !important;
        }
        
        /* Metrics */
        .stMetric {
            background: rgba(40, 167, 69, 0.05);
            border-radius: 8px;
            padding: 12px;
            border: 1px solid rgba(40, 167, 69, 0.1);
        }
        
        /* Success banner */
        .element-container:has(.stSuccess) {
            border-left: 4px solid #28a745;
        }
        
        /* Info boxes */
        .stAlert {
            border-radius: 8px !important;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1b2a, #1b2838);
        }
        
        [data-testid="stSidebar"] .stButton > button {
            width: 100% !important;
        }
        
        /* Progress bar */
        .stProgress > div > div {
            background: linear-gradient(135deg, #28a745, #20c997) !important;
        }
    </style>
    """, unsafe_allow_html=True)

def green_button_link(label, page):
    """Create a prominent green button that links to another page."""
    st.page_link(page, label=label)


