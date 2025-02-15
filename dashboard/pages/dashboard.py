import streamlit as st

def show(set_page):
    st.markdown('<div class="title"><img src="https://file.notion.so/f/f/39b5c584-5e26-4a4a-b692-8e788fe8cbad/717908c1-4544-4872-8400-5de7cbe9cdd4/Logo-removebg-preview.png?table=block&id=19b239ed-c5f1-8072-8ec9-eda9b4d53f7b&spaceId=39b5c584-5e26-4a4a-b692-8e788fe8cbad&expirationTimestamp=1739628000000&signature=VPIsaehhM8A5QOHNHICTut9q5rGAHg4x04T3HPKEPqA&downloadName=Logo-removebg-preview.png" alt="Logo" /></div>', unsafe_allow_html=True)
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
