import streamlit as st
import pandas as pd
import requests
import json

# Cache untuk menghindari pengambilan data yang berulang
@st.cache_data
def fetch_template():
    #Mengambil template dari FastAPI dan meng-cache hasilnya.
    template_url = "http://127.0.0.1:8000/download-template"
    response = requests.get(template_url)
    
    if response.status_code == 200:
        return response.content
    else:
        st.error("❌ Error: Gagal mengunduh template dari API.")
        return None

def show(set_page):
    st.title("📤 Upload File XLSX untuk Prediksi Massal")
    
    # Tombol Download Template dengan cache
    template_data = fetch_template()
    if template_data:
        st.download_button(
            label="📥 Download Template XLSX",
            data=template_data,
            file_name="Mass_Input_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    uploaded_file = st.file_uploader("Pilih file XLSX", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        
        # Debugging: Tampilkan kolom yang ditemukan di dataframe
        # st.write("📄 **Kolom yang ditemukan dalam file Excel:**")
        # st.write(df.columns.tolist())  # Menampilkan daftar nama kolom
        
        # Normalisasi nama kolom untuk menghapus spasi ekstra
        df.columns = df.columns.str.strip()
        
        expected_columns = [
            "Full Name", "City Development Index", "Data Science Experience", "Enrolled University",
            "Education Level", "Work Experience", "Company Size", "Duration of Last New Job",
            "Gender", "Major Discipline", "Company Type"
        ]
        
        # Cek apakah semua kolom yang diharapkan ada dalam dataframe
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.error(f"❌ Error: Kolom berikut tidak ditemukan dalam file Excel: {missing_columns}")
            return
        
        # Cek apakah ada data yang kosong di dalam dataframe
        if df.isnull().values.any():
            st.error("❌ Error: Terdapat data yang kosong dalam file Excel. Harap lengkapi semua kolom sebelum mengunggah.")
            return
        
        st.success("✅ Semua kolom sesuai, siap untuk diproses.")
        st.dataframe(df)  # Tampilkan dataframe yang di-load untuk validasi manual
        
        # Mengirim semua data mentah ke FastAPI
        if st.button("🚀 Prediksi Semua Data"):
            url = "http://127.0.0.1:8000/predict"
            
            data = [
                {
                    "fullname": row["Full Name"],
                    "features": row[expected_columns[1:]].astype(str).tolist()  
                }
                for _, row in df.iterrows()
            ]
            
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                predictions = response.json()["predictions"]
                df["Hasil Prediksi"] = ["💼 Mencari Pekerjaan Baru" if pred["prediction"] == 1 else "🏢 Tidak Mencari Pekerjaan Baru" for pred in predictions]
                st.success("✅ Prediksi Berhasil!")
                st.dataframe(df)
            else:
                st.error(f"Error: {response.text}")
    if st.button("⬅️ Kembali ke Dashboard"):
        set_page("dashboard")
