import streamlit as st
import pandas as pd
import requests
import json
import io

def show(set_page):
    st.title("📤 Upload File XLSX untuk Prediksi Massal")
    
    # Generate template file with example data
    template_data = {
        "city_development_index": [0.92],
        "relevant_experience": [1],
        "enrolled_university": [2],
        "education_level": [3],
        "experience": [5],
        "company_size": [2],
        "last_new_job": [1],
        "gender_Female": [0],
        "gender_Male": [1],
        "major_discipline_Arts": [0],
        "major_discipline_Business Degree": [0],
        "major_discipline_Humanities": [0],
        "major_discipline_No Major": [0],
        "major_discipline_STEM": [1],
        "company_type_Early Startup": [0],
        "company_type_Funded Startup": [0],
        "company_type_NGO": [0],
        "company_type_Public Sector": [0],
        "company_type_Pvt Ltd": [1]
    }
    template_df = pd.DataFrame(template_data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        template_df.to_excel(writer, index=False, sheet_name="Template")
    output.seek(0)
    
    st.download_button(
        label="📥 Download Template XLSX",
        data=output.getvalue(),
        file_name="template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    uploaded_file = st.file_uploader("Pilih file XLSX", type=["xlsx"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
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
