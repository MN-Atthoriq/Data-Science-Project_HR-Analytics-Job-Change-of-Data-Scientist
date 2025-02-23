import streamlit as st

def show(set_page):
    st.markdown('<div class="title"><img src="https://raw.githubusercontent.com/MN-Atthoriq/Data-Science-Project_HR-Analytics-Job-Change-of-Data-Scientist/refs/heads/master-renato/dashboard/img/Logo-removebg-preview.png?token=GHSAT0AAAAAAC4K6WA7ZPKUR72DGCVRNI54Z52USCA" alt="Logo" /></div>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Machine Learning - Predicting Employees Looking for New Jobs</p>', unsafe_allow_html=True)

    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col2:
        if st.button("📥 Input Manual"):
            set_page("manual")
    with col3:
        if st.button("📁 Upload CSV"):
            set_page("upload")
    st.markdown("</div>", unsafe_allow_html=True)
