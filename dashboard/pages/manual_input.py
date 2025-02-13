import streamlit as st
import requests
import json


def show(set_page):
    st.title("📥 Input Data Karyawan Secara Manual")
    feature_names = [
        "city_development_index", "relevant_experience", "enrolled_university",
        "education_level", "experience", "company_size", "last_new_job",
        "gender_Female", "gender_Male", "major_discipline_Arts",
        "major_discipline_Business Degree", "major_discipline_Humanities",
        "major_discipline_No Major", "major_discipline_STEM",
        "company_type_Early Startup", "company_type_Funded Startup",
        "company_type_NGO", "company_type_Public Sector", "company_type_Pvt Ltd"
    ]
    features = [st.number_input(f"{name}", value=0.0) for name in feature_names]
    if st.button("🔍 Prediksi"):
        url = "http://127.0.0.1:8000/predict"
        data = [{"features": features}]
        response = requests.post(url, data=json.dumps(data))
        if response.status_code == 200:
            prediction = response.json()["predictions"][0]
            hasil = "💼 Mencari Pekerjaan Baru" if prediction == 1 else "🏢 Tidak Mencari Pekerjaan Baru"
            st.success(f"Hasil Prediksi: {hasil}")
        else:
            st.error(f"Error: {response.text}")

    if st.button("⬅️ Kembali ke Dashboard"):
        set_page("dashboard")
