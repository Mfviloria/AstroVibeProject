from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)
CORS(app)

# --- Cargar modelo ML ---
model = joblib.load("ML/exoplanet_classifier.joblib")
encoder = joblib.load("ML/label_encoder.joblib")
scaler = joblib.load("ML/scaler.joblib")

# --- Cargar datos de exoplanetas ---
df = pd.read_csv("exoplanets_visual.csv")
exoplanetas = df.to_dict(orient="records")

# Endpoint para enviar datos de exoplanetas al frontend
@app.route("/exoplanets", methods=["GET"])
def get_exoplanets():
    return jsonify(exoplanetas)

# Endpoint para predecir un nuevo exoplaneta
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    try:
        features = np.array([[
            data["snr"], data["radius"], data["sma"], data["temp"], 
            data["period"], data["duration"], data["depth"],
            data["steff"], data["slogg"], data["sr"], data["time0bk"]
        ]])
        scaled = scaler.transform(features)
        pred = model.predict(scaled)
        label = encoder.inverse_transform(pred)[0]
        return jsonify({"prediction": label})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
