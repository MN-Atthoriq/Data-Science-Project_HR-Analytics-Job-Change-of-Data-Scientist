import streamlit as st
import pandas as pd
import requests
import json

def show(set_page):
    st.title("📤 Upload File CSV untuk Prediksi Massal")
    uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("📄 **Data yang Di-upload:**")
        st.dataframe(df)
        if st.button("🚀 Prediksi Semua Data"):
            url = "http://127.0.0.1:8000/predict"
            data = [{"features": row.tolist()} for _, row in df.iterrows()]
            response = requests.post(url, data=json.dumps(data))
            if response.status_code == 200:
                predictions = response.json()["predictions"]
                df["Hasil Prediksi"] = ["💼 Mencari Pekerjaan Baru" if pred == 1 else "🏢 Tidak Mencari Pekerjaan Baru" for pred in predictions]
                st.success("✅ Prediksi Berhasil!")
                st.dataframe(df)
            else:
                st.error(f"Error: {response.text}")

    if st.button("⬅️ Kembali ke Dashboard"):
        set_page("dashboard")
