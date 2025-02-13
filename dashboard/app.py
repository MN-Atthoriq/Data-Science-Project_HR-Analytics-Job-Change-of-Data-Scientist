# app.py
import streamlit as st
from pathlib import Path
from pages import dashboard, manual_input, upload_csv

# ================== 🎨 CUSTOM PAGE CONFIGURATION ==================
st.set_page_config(
    page_title="Ascencio - Dashboard",
    page_icon="✨",
    layout="wide"
)

# ✅ Inisialisasi Session State
if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"

 # ================== 🎨 Custom CSS Dictionary ==================
CSS_STYLES = {
    "dashboard": """
    <style>
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stSidebar"] {display: none; !important;}
    [data-testid="stSidebarCollapsedControl"] {display: none; !important;}

    

    .stApp {
        background: #000000;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .navbar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 60px;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        padding: 0 20px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        z-index: 1000;
    }
    .navbar a {
        text-decoration: none;
        font-size: 42px;
        color: #ffffff;
        font-weight: bold;
    }
    .title {
        display: flex;
        justify-content: center;
    }
    img{
        height: 250px; 
        width: 400px;
    }
    .subtitle {
        text-align: center;
        color: #f1d7d7;
        font-style: italic;
        font-size: 16px;
    }
    .button-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 30px;
        margin-top: 30px;
    }
    div.stButton {
        display: flex;
        justify-content: center;
    }
    
    div.stButton > button {
        background-color: white;
        color: black;
        font-size: 64px;
        font-weight: bold;
        border-radius: 15px;
        width: 400px;
        height: 200px;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.15);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
     div.stButton > button p{
        color: black;
        font-size: 48px;
        font-weight: bold;
    } 

    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0px 6px 18px rgba(0, 0, 0, 0.3);
    }
    </style>
    <div class="navbar">
        <a href="#">Ascencio</a>
    </div>
    """,
    "manual": """
        <style>
        [data-testid="stToolbar"] { display: none !important; }
        [data-testid="stHeader"] { display: none !important; }
        [data-testid="stSidebar"] {display: none; !important;}
        [data-testid="stSidebarCollapsedControl"] {display: none; !important;}
        </style>
    """,
    "upload": """
        <style>
        [data-testid="stToolbar"] { display: none !important; }
        [data-testid="stHeader"] { display: none !important; }
        [data-testid="stSidebar"] {display: none; !important;}
        [data-testid="stSidebarCollapsedControl"] {display: none; !important;}
        </style>
    """
}

# ================== 📌 Fungsi Load CSS ==================
def load_css(page):
    if page in CSS_STYLES:
        st.markdown(CSS_STYLES[page], unsafe_allow_html=True)
    else:
        st.error(f"⚠️ Style untuk halaman '{page}' tidak ditemukan!")

load_css(st.session_state["page"])
# ================== 🎯 NAVIGATION SYSTEM ==================
def set_page(page):
    st.session_state["page"] = page
    st.rerun()

# ================== 🔄 PAGE RENDERING ==================
if st.session_state["page"] == "dashboard":
    dashboard.show(set_page)
elif st.session_state["page"] == "manual":
    manual_input.show(set_page)
elif st.session_state["page"] == "upload":
    upload_csv.show(set_page)
