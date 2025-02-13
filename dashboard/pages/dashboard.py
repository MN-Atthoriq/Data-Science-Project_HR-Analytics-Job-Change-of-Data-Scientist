import streamlit as st

def show(set_page):
    st.markdown('<div class="title"><img src="https://cdn.discordapp.com/attachments/1160633619455426724/1339569209197330484/Logo-removebg-preview.png?ex=67af328b&is=67ade10b&hm=7ce5a687a63243e1ae26356278cc31a7b9c7f65f3e9840d269045299cc024144&" alt="Logo" /></div>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Machine Learning - Predicting Employees Looking for New Jobs</p>', unsafe_allow_html=True)

    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("📥 Input Manual"):
            set_page("manual")
    with col2:
        if st.button("📁 Upload CSV"):
            set_page("upload")
    st.markdown("</div>", unsafe_allow_html=True)
