from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
from typing import List

# Inisialisasi FastAPI
app = FastAPI()

# Load model XGBClassifier
model = joblib.load('app/model/model.pkl')

# Coba dapatkan jumlah fitur yang diharapkan model
try:
    expected_feature_count = len(model.get_booster().feature_names)
except:
    expected_feature_count = model.n_features_in_  # Alternatif jika get_booster() tidak ada

# Skema data untuk satu input
class InputData(BaseModel):
    features: List[float]  # List untuk satu baris data

# Endpoint untuk cek status API
@app.get("/")
def read_root():
    return {"message": "API XGBClassifier berjalan dengan baik!"}

# Endpoint untuk prediksi banyak data
@app.post("/predict")
def predict(data: List[InputData]):  # Menerima list dari InputData
    try:
        # Konversi semua data input menjadi array numpy
        features = np.array([item.features for item in data])
        
        # Validasi jumlah fitur
        if features.shape[1] != expected_feature_count:
            raise ValueError(f"Expected {expected_feature_count} features, got {features.shape[1]}")

        # Prediksi untuk semua data
        predictions = model.predict(features)

        # Mengembalikan hasil prediksi sebagai list
        return {"predictions": predictions.tolist()}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saat memproses data: {e}")
