from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import logging
from typing import List

# Inisialisasi FastAPI
app = FastAPI()

# Load model XGBClassifier
model = joblib.load('app/model/model.pkl')

# Logging untuk debugging
logging.basicConfig(level=logging.INFO)

# Mapping kategori ke angka
enrolled_university_map = {"No Enroll": 0, "Part Time": 1, "Full Time": 2}
relevant_experience_map = {"No": 0, "Yes": 1}
education_level_map = {"Primary School": 0, "High School": 1, "Graduate": 2, "Masters": 3, "Phd": 4}
company_size_map = {
    "Less than 10": 0, "10 to 49": 1, "50 to 99": 2, "100 to 499": 3,
    "500 to 999": 4, "1000 to 4999": 5, "5000 to 9999": 6, "More than 9999": 7
}

gender_map = {"Male": [0, 1], "Female": [1, 0], "Other": [0, 0]}
major_discipline_map = {
    "Arts": [1, 0, 0, 0, 0],
    "Business Degree": [0, 1, 0, 0, 0],
    "Humanities": [0, 0, 1, 0, 0],
    "No Major": [0, 0, 0, 1, 0],
    "STEM": [0, 0, 0, 0, 1]
}
company_type_map = {
    "Early Startup": [1, 0, 0, 0, 0],
    "Funded Startup": [0, 1, 0, 0, 0],
    "NGO": [0, 0, 1, 0, 0],
    "Public Sector": [0, 0, 0, 1, 0],
    "Pvt Ltd": [0, 0, 0, 0, 1]
}

# Skema data untuk satu input
class InputData(BaseModel):
    fullname: str
    features: List[str]  # Semua fitur dalam bentuk string

# Endpoint untuk cek status API
@app.get("/")
def read_root():
    return {"message": "API LGBMClassifier berjalan dengan baik!"}

# Fungsi untuk encoding data kategori menjadi numerik
def encode_features(raw_features: List[str]) -> List[float]:
    try:
        logging.info(f"Raw features received: {raw_features}")

        # Konversi fitur numerik
        city_development_index = float(raw_features[0])
        relevant_experience = relevant_experience_map.get(raw_features[1], 0)
        enrolled_university = enrolled_university_map.get(raw_features[2], 0)
        education_level = education_level_map.get(raw_features[3], 0)
        experience = int(raw_features[4])
        company_size = company_size_map.get(raw_features[5], 0)
        last_new_job = int(raw_features[6])

        # Encoding gender
        gender_value = raw_features[7]
        gender_encoded = gender_map.get(gender_value, [0, 0])

        # Encoding major_discipline
        major_discipline_value = raw_features[8]
        major_discipline_encoded = major_discipline_map.get(major_discipline_value, [0, 0, 0, 0, 0])

        # Encoding company_type
        company_type_value = raw_features[9]
        company_type_encoded = company_type_map.get(company_type_value, [0, 0, 0, 0, 0])

        # Gabungkan semua fitur menjadi satu list
        encoded_features = [
            city_development_index, relevant_experience, enrolled_university, education_level,
            experience, company_size, last_new_job
        ] + gender_encoded + major_discipline_encoded + company_type_encoded

        logging.info(f"Encoded features: {encoded_features}")
        return encoded_features
    except Exception as e:
        raise ValueError(f"Error encoding features: {e}")

# Endpoint untuk prediksi banyak data
@app.post("/predict")
def predict(data: List[InputData]):
    try:
        logging.info(f"Request data: {data}")

        # Encoding semua data input menjadi format numerik
        features = np.array([encode_features(item.features) for item in data])

        # Validasi jumlah fitur
        expected_feature_count = 19
        if features.shape[1] != expected_feature_count:
            raise ValueError(f"Expected {expected_feature_count} features, got {features.shape[1]}")

        # Prediksi untuk semua data
        predictions = model.predict(features)

        return {
            "predictions": [
                {"fullname": item.fullname, "prediction": int(pred)}
                for item, pred in zip(data, predictions)
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saat memproses data: {e}")
