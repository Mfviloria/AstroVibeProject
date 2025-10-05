from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
from openai import OpenAI
import subprocess
import sys
import pandas as pd

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in exoplanets. Answer clearly in English."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=300
        )
        bot_message = response.choices[0].message.content
        return jsonify({"response": bot_message})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"}), 500

@app.route("/exoplanets")
def exoplanets():
    df = pd.read_csv("exoplanets_visual.csv")

    # Normalizar RA y Dec al rango 0-1 para el canvas
    df['x'] = (df['ra'] - df['ra'].min()) / (df['ra'].max() - df['ra'].min())
    df['y'] = (df['dec'] - df['dec'].min()) / (df['dec'].max() - df['dec'].min())

    # Seleccionar solo las columnas necesarias
    data = df[['x', 'y', 'pl_rade', 'hostname']].to_dict(orient="records")
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)