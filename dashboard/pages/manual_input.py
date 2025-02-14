import streamlit as st
import requests
import json

def show(set_page):
    st.markdown(
        """
        <style>
        .manual-input-container {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            color: white;
            width: 70%;
            margin: auto;
        }
        .input-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        .input-column {
            width: 48%;
        }
        .input-label {
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 5px;
            display: block;
        }
        .input-box {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
            background: #333;
            color: white;
        }
        .predict-button {
            background-color: #4CAF50;
            color: white;
            font-size: 18px;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px;
            width: 100%;
            text-align: center;
            transition: 0.3s;
            cursor: pointer;
            border: none;
        }
        .predict-button:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="manual-input-container">', unsafe_allow_html=True)
    st.title("📥 Input Data Karyawan Secara Manual")
    
    feature_inputs = {}
    
    cols = st.columns(2)
    
    with cols[0]:
        feature_inputs["city_development_index"] = st.number_input("City Development Index", value=0.0, step=0.01, format="%.3f")
        feature_inputs["relevant_experience"] = st.selectbox("Relevant Experience", options=[0, 1])
        feature_inputs["gender"] = st.selectbox("Gender (0: Male, 1: Female)", options=[0, 1])
        feature_inputs["enrolled_university"] = st.selectbox("Enrolled University", options=[0, 1, 2])
        feature_inputs["education_level"] = st.selectbox("Education Level", options=[0, 1, 2, 3, 4])
    
    with cols[1]:
        feature_inputs["experience"] = st.number_input("Experience", value=0, step=1, min_value=0)
        feature_inputs["company_size"] = st.number_input("Company Size", value=0, step=1, min_value=0)
        feature_inputs["last_new_job"] = st.number_input("Last New Job", value=0, step=1, min_value=0)
        feature_inputs["major_discipline"] = st.selectbox("Major Discipline", options=[
            "major_discipline_Arts", "major_discipline_Business Degree", "major_discipline_Humanities", 
            "major_discipline_No Major", "major_discipline_STEM"])
        feature_inputs["company_type"] = st.selectbox("Company Type", options=[
            "company_type_Early Startup", "company_type_Funded Startup", "company_type_NGO", 
            "company_type_Public Sector", "company_type_Pvt Ltd"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🔍 Prediksi", key="predict", help="Klik untuk memulai prediksi", use_container_width=True):
        json_payload = {
            "features": [
                feature_inputs["city_development_index"],
                feature_inputs["relevant_experience"],
                feature_inputs["enrolled_university"],
                feature_inputs["education_level"],
                feature_inputs["experience"],
                feature_inputs["company_size"],
                feature_inputs["last_new_job"],
                1 if feature_inputs["gender"] == 1 else 0,
                0 if feature_inputs["gender"] == 1 else 1,
            ] + [1 if feature_inputs["major_discipline"] == md else 0 for md in [
                "major_discipline_Arts", "major_discipline_Business Degree", "major_discipline_Humanities", 
                "major_discipline_No Major", "major_discipline_STEM"]] + [
                1 if feature_inputs["company_type"] == ct else 0 for ct in [
                "company_type_Early Startup", "company_type_Funded Startup", "company_type_NGO", 
                "company_type_Public Sector", "company_type_Pvt Ltd"]]
        }
        
        url = "http://127.0.0.1:8000/predict"
        response = requests.post(url, data=json.dumps([json_payload]))
        
        if response.status_code == 200:
            prediction = response.json()["predictions"][0]
            hasil = "💼 Mencari Pekerjaan Baru" if prediction == 1 else "🏢 Tidak Mencari Pekerjaan Baru"
            st.success(f"Hasil Prediksi: {hasil}")
        else:
            st.error(f"Error: {response.text}")
    
    if st.button("⬅️ Kembali ke Dashboard", key="back", use_container_width=True):
        set_page("dashboard")
