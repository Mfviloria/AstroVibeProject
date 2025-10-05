import streamlit as st
import pandas as pd
import joblib
import os
import plotly.express as px

st.set_page_config(page_title="Simulador y Clasificador de Exoplanetas", layout="wide")

st.title("Simulador y Clasificador de Exoplanetas")

st.sidebar.header("Navegación")
page = st.sidebar.selectbox("Selecciona una sección:", ["Simulador 2D", "Clasificador ML"])

if page == "Simulador 2D":
    st.header("Simulador 2D")
    st.write("Aquí puedes mostrar tu simulador 2D. Puedes adaptar este espacio para mostrar visualizaciones, cargar datos, etc.")
    # Construir rutas relativas al archivo actual para evitar problemas con el cwd
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "ML", "exoplanets_visual.csv")
    if os.path.exists(data_path):
        try:
            df = pd.read_csv(data_path)
            # Preparar datos para visualización 2D
            # Normalizar RA y Dec al rango 0-1 para visualización en canvas
            if 'ra' in df.columns and 'dec' in df.columns:
                df = df.copy()
                df['x'] = (df['ra'] - df['ra'].min()) / (df['ra'].max() - df['ra'].min())
                df['y'] = (df['dec'] - df['dec'].min()) / (df['dec'].max() - df['dec'].min())
            else:
                df['x'] = 0
                df['y'] = 0

            # Asegurar que la columna del radio exista y tenga valores numéricos
            if 'pl_rade' in df.columns:
                df['pl_rade'] = pd.to_numeric(df['pl_rade'], errors='coerce').fillna(0.5)
            else:
                df['pl_rade'] = 0.5

            st.subheader("Tabla de ejemplo")
            st.dataframe(df.head())

            st.subheader("Visualización 2D interactiva")
            # Control para tamaño de puntos
            size_scale = st.sidebar.slider("Escala de tamaño de puntos", 1.0, 50.0, 10.0)

            # Crear figura con Plotly
            try:
                fig = px.scatter(
                    df,
                    x='x',
                    y='y',
                    size=df['pl_rade'] * size_scale,
                    color='discoverymethod' if 'discoverymethod' in df.columns else None,
                    hover_data=['pl_name', 'hostname', 'pl_rade', 'pl_orbper'] if 'pl_name' in df.columns else None,
                    title='Distribución 2D de exoplanetas (RA/Dec normalizados)',
                    labels={'x': 'RA (normalizado)', 'y': 'Dec (normalizado)'}
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creando la visualización: {e}")
        except Exception as e:
            st.error(f"Error leyendo el CSV en {data_path}: {e}")
    else:
        st.info(f"No se encontró el archivo de datos para el simulador 2D. Se buscó en: {data_path}")

elif page == "Clasificador ML":
    st.header("Clasificador de Exoplanetas (ML)")
    st.write("Introduce los datos de un exoplaneta para predecir su clase.")
    try:
        # Cargar modelos usando rutas relativas al archivo para mayor robustez
        base_dir = os.path.dirname(__file__)
        model = joblib.load(os.path.join(base_dir, "ML", "exoplanet_classifier.joblib"))
        scaler = joblib.load(os.path.join(base_dir, "ML", "scaler.joblib"))
        encoder = joblib.load(os.path.join(base_dir, "ML", "label_encoder.joblib"))
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
