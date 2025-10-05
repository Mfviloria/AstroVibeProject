import streamlit as st
import pandas as pd
import joblib
import os

st.set_page_config(page_title="Simulador y Clasificador de Exoplanetas", layout="wide")

st.title("Simulador y Clasificador de Exoplanetas")

st.sidebar.header("Navegación")
page = st.sidebar.selectbox("Selecciona una sección:", ["Simulador 2D", "Clasificador ML"])

if page == "Simulador 2D":
    st.header("Simulador 2D")
    st.write("Aquí puedes mostrar tu simulador 2D. Puedes adaptar este espacio para mostrar visualizaciones, cargar datos, etc.")
    if os.path.exists("ML/exoplanets_visual.csv"):
        df = pd.read_csv("ML/exoplanets_visual.csv")
        st.dataframe(df.head())
    else:
        st.info("No se encontró el archivo de datos para el simulador 2D.")

elif page == "Clasificador ML":
    st.header("Clasificador de Exoplanetas (ML)")
    st.write("Introduce los datos de un exoplaneta para predecir su clase.")
    try:
        model = joblib.load("ML/exoplanet_classifier.joblib")
        scaler = joblib.load("ML/scaler.joblib")
        encoder = joblib.load("ML/label_encoder.joblib")
        st.subheader("Introduce los datos del exoplaneta:")
        # Los 11 features en orden:
        # koi_model_snr, koi_prad, koi_sma, koi_teq, koi_period, koi_duration, koi_depth, koi_steff, koi_slogg, koi_srad, koi_time0bk
        with st.form("exoplanet_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                koi_model_snr = st.number_input("Transit Signal-to-Noise (koi_model_snr)", value=18.0)
                koi_prad = st.number_input("Planetary Radius (koi_prad)", value=0.59)
                koi_sma = st.number_input("Orbit Semi-Major Axis [au] (koi_sma)", value=0.0739)
                koi_teq = st.number_input("Equilibrium Temperature [K] (koi_teq)", value=443.0)
            with col2:
                koi_period = st.number_input("Orbital Period [days] (koi_period)", value=10.3128)
                koi_duration = st.number_input("Transit Duration [hrs] (koi_duration)", value=3.2)
                koi_depth = st.number_input("Transit Depth [ppm] (koi_depth)", value=0.45)
                koi_steff = st.number_input("Stellar Effective Temperature [K] (koi_steff)", value=5600.0)
            with col3:
                koi_slogg = st.number_input("Stellar Surface Gravity [log10(cm/s**2)] (koi_slogg)", value=4.4)
                koi_srad = st.number_input("Stellar Radius [Solar radii] (koi_srad)", value=0.98)
                koi_time0bk = st.number_input("Transit Epoch [BKJD] (koi_time0bk)", value=2459000.123)
            submitted = st.form_submit_button("Predecir clase")
        if submitted:
            features = [[
                koi_model_snr, koi_prad, koi_sma, koi_teq, koi_period,
                koi_duration, koi_depth, koi_steff, koi_slogg, koi_srad, koi_time0bk
            ]]
            X_scaled = scaler.transform(features)
            pred = model.predict(X_scaled)
            clase = encoder.inverse_transform(pred)
            st.success(f"Predicción: {clase[0]}")
    except Exception as e:
        st.error(f"Error cargando el modelo o scaler: {e}")
