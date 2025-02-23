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

    st.title("📥 Input Data Karyawan Secara Manual")
    
    fullname = st.text_input("Full Name")
    
    feature_inputs = {}
    cols = st.columns(2)
    
    with cols[0]:
        feature_inputs["Gender"] = st.selectbox("Gender", options=["Male", "Female", "Other"], index=None, placeholder="Pilih opsi")
        feature_inputs["Experience"] = st.number_input("Work Experience", value=0, step=1, min_value=0, max_value=21)
        feature_inputs["Last New Job"] = st.number_input("Duration of Last New Job", value=0, step=1, min_value=0)
        feature_inputs["Major Discipline"] = st.selectbox("Major Discipline", options=["Arts", "Business Degree", "Humanities", "No Major", "STEM"], index=None, placeholder="Pilih opsi")
        feature_inputs["Company Size"] = st.selectbox("Company Size", options=[
            "Less than 10", "10 to 49", "50 to 99", "100 to 499", "500 to 999", "1000 to 4999", "5000 to 9999", "More than 9999"], index=None, placeholder="Pilih opsi")
    
    with cols[1]:
        feature_inputs["Enrolled University"] = st.selectbox("Enrolled University", options=["No Enroll", "Part Time", "Full Time"], index=None, placeholder="Pilih opsi")
        feature_inputs["Relevant Experience"] = st.selectbox("Data Science Work Experience", options=["No", "Yes"], index=None, placeholder="Pilih opsi")
        feature_inputs["Education Level"] = st.selectbox("Education Level", options=["Primary School", "High School", "Graduate", "Masters", "Phd"], index=None, placeholder="Pilih opsi")
        feature_inputs["City Development Index"] = st.number_input("City Development Index", value=0.0, step=0.01, format="%.3f")
        feature_inputs["Company Type"] = st.selectbox("Company Type", options=["Early Startup", "Funded Startup", "NGO", "Public Sector", "Pvt Ltd"], index=None, placeholder="Pilih opsi")
    
    if st.button("🔍 Prediksi", key="predict", help="Klik untuk memulai prediksi", use_container_width=True):
        # Validasi agar tidak ada input yang kosong
        if not fullname or any(v is None or v == "" for v in feature_inputs.values()):
            st.error("❌ Error: Semua bidang harus diisi sebelum melakukan prediksi.")
            return
        
        json_payload = {
            "fullname": fullname,
            "features": [
                str(feature_inputs["City Development Index"]),
                feature_inputs["Relevant Experience"],
                feature_inputs["Enrolled University"],
                feature_inputs["Education Level"],
                str(feature_inputs["Experience"]),
                feature_inputs["Company Size"],
                str(feature_inputs["Last New Job"]),
                feature_inputs["Gender"],
                feature_inputs["Major Discipline"],
                feature_inputs["Company Type"]
            ]
        }
        
        url = "http://127.0.0.1:8000/predict"
        response = requests.post(url, json=[json_payload])
        
        if response.status_code == 200:
            prediction = response.json()["predictions"][0]
            hasil = "💼 Mencari Pekerjaan Baru" if prediction["prediction"] == 1 else "🏢 Tidak Mencari Pekerjaan Baru"
            st.success(f"Hasil Prediksi untuk {fullname}: {hasil}")
        else:
            st.error(f"Error: {response.text}")
    
    if st.button("⬅️ Kembali ke Dashboard", key="back", use_container_width=True):
        set_page("dashboard")
