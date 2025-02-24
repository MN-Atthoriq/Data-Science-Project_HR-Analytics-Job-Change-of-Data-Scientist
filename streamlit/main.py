import streamlit as st
import base64
import os

### Function
st.set_page_config(page_title="Ascencio Course Selection", page_icon="🧩", layout="wide")

page_bg_img = '''
<style>
body {
background-image: url("https://images.unsplash.com/photo-1542281286-9e0a16bb7366");
background-size: cover;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)


