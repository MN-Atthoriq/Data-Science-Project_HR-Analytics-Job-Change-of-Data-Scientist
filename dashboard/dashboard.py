import streamlit as st
import pandas as pd
import requests
import json

# Judul Dashboard
st.title("📊 Dashboard Prediksi Karyawan - Inovasi Machine Learning")

# Daftar Fitur Model (tanpa kolom target)
feature_names = [
    "city_development_index",
    "relevant_experience",
    "enrolled_university",
    "education_level",
    "experience",
    "company_size",
    "last_new_job",
    "gender_Female",
    "gender_Male",
    "major_discipline_Arts",
    "major_discipline_Business Degree",
    "major_discipline_Humanities",
    "major_discipline_No Major",
    "major_discipline_STEM",
    "company_type_Early Startup",
    "company_type_Funded Startup",
    "company_type_NGO",
    "company_type_Public Sector",
    "company_type_Pvt Ltd"
]

# Pilihan Mode Input
st.sidebar.title("🔍 Pilih Mode Input")
mode = st.sidebar.radio("Pilih cara input data:", ("Input Manual", "Upload File CSV/Excel"))

# ==========================
# 🚀 1. INPUT MANUAL
# ==========================
if mode == "Input Manual":
    st.header("📝 Masukkan Data Karyawan:")
    features = []

    # Input Manual untuk Setiap Fitur
    features.append(st.number_input("City Development Index (0.0 - 1.0)", min_value=0.0, max_value=1.0, step=0.01))
    features.append(int(st.selectbox("Relevant Experience", [1, 0], format_func=lambda x: "Ya" if x == 1 else "Tidak")))
    features.append(int(st.selectbox("Enrolled University", [0, 1, 2], format_func=lambda x: ["Tidak Terdaftar", "Full Time", "Part Time"][x])))
    features.append(int(st.selectbox("Education Level", [0, 1, 2, 3], format_func=lambda x: ["Primary School", "High School", "Graduate", "Masters"][x])))
    features.append(int(st.number_input("Experience (Tahun)", min_value=0, max_value=50, step=1)))
    features.append(int(st.selectbox("Company Size", [0, 1, 2], format_func=lambda x: ["Kecil", "Menengah", "Besar"][x])))
    features.append(int(st.selectbox("Last New Job (Tahun)", [0, 1, 2, 3], format_func=lambda x: ["<1 Tahun", "1 Tahun", "2 Tahun", ">3 Tahun"][x])))
    features.append(int(st.radio("Gender Female", [1, 0], format_func=lambda x: "Ya" if x == 1 else "Tidak")))
    features.append(int(st.radio("Gender Male", [1, 0], format_func=lambda x: "Ya" if x == 1 else "Tidak")))

    # Major Discipline
    for major in ["Arts", "Business Degree", "Humanities", "No Major", "STEM"]:
        features.append(int(st.radio(f"Major Discipline: {major}", [1, 0], format_func=lambda x: "Ya" if x == 1 else "Tidak")))

    # Company Type
    for c_type in ["Early Startup", "Funded Startup", "NGO", "Public Sector", "Pvt Ltd"]:
        features.append(int(st.radio(f"Company Type: {c_type}", [1, 0], format_func=lambda x: "Ya" if x == 1 else "Tidak")))

    # Tombol Prediksi
    if st.button("🔍 Prediksi"):
        url = "http://127.0.0.1:8000/predict"
        data = [{"features": features}]  # Format untuk batch prediksi

        try:
            response = requests.post(url, data=json.dumps(data))
            if response.status_code == 200:
                prediction = response.json()["predictions"][0]
                hasil = "💼 Mencari Pekerjaan Baru" if prediction == 1 else "🏢 Tidak Mencari Pekerjaan Baru"
                st.success(f"Hasil Prediksi: {hasil}")
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

# ==========================
# 📊 2. UPLOAD FILE CSV/EXCEL
# ==========================
else:
    st.header("📥 Upload File CSV atau Excel")
    uploaded_file = st.file_uploader("Pilih file CSV atau Excel", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            # Membaca file yang di-upload
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Tampilkan data yang di-upload
            st.write("📄 **Data yang Di-upload:**")
            st.dataframe(df)

            # Validasi kolom
            missing_columns = [col for col in feature_names if col not in df.columns]
            if missing_columns:
                st.error(f"❌ Kolom berikut tidak ditemukan: {', '.join(missing_columns)}")
            else:
                # Kirim data ke API untuk prediksi batch
                data = [{"features": row.tolist()} for index, row in df.iterrows()]

                if st.button("🚀 Prediksi Data"):
                    url = "http://127.0.0.1:8000/predict"
                    response = requests.post(url, data=json.dumps(data))

                    if response.status_code == 200:
                        predictions = response.json()["predictions"]
                        df["Hasil Prediksi"] = ["💼 Mencari Pekerjaan Baru" if pred == 1 else "🏢 Tidak Mencari Pekerjaan Baru" for pred in predictions]

                        # Tampilkan hasil prediksi
                        st.success("✅ Prediksi Berhasil!")
                        st.dataframe(df)
                    else:
                        st.error(f"Error: {response.text}")

        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file: {e}")
