import streamlit as st
import pandas as pd
import joblib
import os
import requests
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Simulador y Clasificador de Exoplanetas", layout="wide")

st.title("Simulador y Clasificador de Exoplanetas")

st.sidebar.header("Navegación")
# Páginas disponibles
page = st.sidebar.selectbox("Selecciona una sección:", ["Simulador 2D", "Simulador 3D", "Clasificador ML"])

# --- Asistente virtual para usuarios noveles (barra lateral) ---
if 'assistant_messages' not in st.session_state:
    st.session_state.assistant_messages = [
        ("bot", "Hola 👋, soy el asistente. Puedo ayudarte a usar el simulador 2D/3D y el clasificador. Pregunta cosas como: '¿Cómo cargo datos?' o '¿Cómo agrego un exoplaneta?'.")
    ]

def generate_fallback_reply(user_text: str) -> str:
    t = user_text.lower()
    if '3d' in t or '3 d' in t:
        return "Para usar el simulador 3D: ve a 'Simulador 3D' desde el menú y usa los controles para ajustar la escala y colores. Si no ves puntos, comprueba que el CSV 'ML/exoplanets_visual.csv' existe."
    if '2d' in t:
        return "En 'Simulador 2D' puedes ver la distribución en RA/Dec. Usa el formulario para agregar un exoplaneta y el botón de predicción si tienes los modelos en la carpeta ML/."
    if 'csv' in t or 'datos' in t:
        return "El archivo de datos esperado está en 'Pagina_web_en_24/ML/exoplanets_visual.csv'. Si no existe, copia el CSV allí o actualiza la ruta en el código."
    if 'modelo' in t or 'model' in t or 'predict' in t:
        return "Para habilitar predicciones ML debes tener 'exoplanet_classifier.joblib', 'scaler.joblib' y 'label_encoder.joblib' en la carpeta ML/. Si no están, el formulario seguirá permitiendo añadir exoplanetas pero sin predicción."
    return "Puedo ayudarte con: cómo usar los simuladores 2D/3D, cómo añadir exoplanetas, o cómo preparar los archivos ML. Fórmulate una pregunta concreta o escribe 'ayuda'."

with st.sidebar.expander("Asistente para principiantes 🤖", expanded=False):
    for role, msg in st.session_state.assistant_messages:
        if role == 'bot':
            st.markdown(f"**Asistente:** {msg}")
        else:
            st.markdown(f"**Tú:** {msg}")

    with st.form("assistant_form"):
        user_input = st.text_input("Escribe tu pregunta para el asistente:")
        sent = st.form_submit_button("Enviar")
    if sent and user_input:
        st.session_state.assistant_messages.append(("user", user_input))
        # Intentar pedir al backend local (/chat)
        reply = None
        try:
            resp = requests.post("http://127.0.0.1:5000/chat", json={"message": user_input}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                reply = data.get('response')
            else:
                reply = None
        except Exception:
            reply = None

        if not reply:
            reply = generate_fallback_reply(user_input)

        st.session_state.assistant_messages.append(("bot", reply))
        st.experimental_rerun()

if page == "Simulador 2D":
    st.header("Simulador 2D")
    st.write("Aquí puedes mostrar tu simulador 2D. Puedes adaptar este espacio para mostrar visualizaciones, cargar datos, etc.")
    # Construir rutas relativas al archivo actual para evitar problemas con el cwd
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "ML", "exoplanets_visual.csv")
    if os.path.exists(data_path):
        try:
            df = pd.read_csv(data_path)
        except Exception as e:
            st.error(f"Error leyendo el CSV en {data_path}: {e}")
            df = pd.DataFrame()
    else:
        st.info(f"No se encontró el archivo de datos para el simulador 2D. Se buscó en: {data_path}")
        df = pd.DataFrame()

    # Cargar KOI para información adicional (si existe)
    koi_path = os.path.join(base_dir, "ML", "koi_completo.csv")
    koi_dict = {}
    if os.path.exists(koi_path):
        try:
            koi_df = pd.read_csv(koi_path)
            koi_ex = koi_df.to_dict(orient="records")
            koi_dict = {str(k.get('kepoi_name')): k for k in koi_ex}
        except Exception:
            koi_dict = {}

    # Normalizar y preparar columnas necesarias
    if not df.empty:
        df = df.copy()
        if 'ra' in df.columns and 'dec' in df.columns:
            df['x'] = (df['ra'] - df['ra'].min()) / (df['ra'].max() - df['ra'].min())
            df['y'] = (df['dec'] - df['dec'].min()) / (df['dec'].max() - df['dec'].min())
        else:
            df['x'] = 0.0
            df['y'] = 0.0
        if 'pl_rade' in df.columns:
            df['pl_rade'] = pd.to_numeric(df['pl_rade'], errors='coerce').fillna(0.5)
        else:
            df['pl_rade'] = 0.5
    else:
        # DataFrame vacío: crear columnas mínimas
        df = pd.DataFrame(columns=['pl_name', 'hostname', 'ra', 'dec', 'pl_rade', 'pl_eqt', 'x', 'y'])

    # Inicializar estado de sesión con el dataframe
    if 'exo_df' not in st.session_state:
        st.session_state.exo_df = df

    exo_df = st.session_state.exo_df

    # Intentar cargar modelos (opcional) para predicción al añadir
    model, scaler, encoder = None, None, None
    try:
        model = joblib.load(os.path.join(base_dir, "ML", "exoplanet_classifier.joblib"))
        scaler = joblib.load(os.path.join(base_dir, "ML", "scaler.joblib"))
        encoder = joblib.load(os.path.join(base_dir, "ML", "label_encoder.joblib"))
    except Exception:
        # no hay modelo disponible; la sección de clasificación seguirá funcionando en su propio tab
        model = scaler = encoder = None

    # UI: Dos columnas, a la izquierda controles/tabla, a la derecha visualización
    left, right = st.columns([1, 2])

    with left:
        st.subheader("Agregar nuevo exoplaneta")
        with st.form("add_exo_form"):
            name = st.text_input("Nombre")
            ra = st.number_input("RA (0-360)", value=0.0)
            dec = st.number_input("Dec (-90 a 90)", value=0.0)
            rade = st.number_input("Radio R⊕", value=1.0)
            eqt = st.number_input("Temperatura K", value=0.0)
            snr = st.number_input("Transit Signal-to-Noise", value=10.0)
            sma = st.number_input("Orbit Semi-major Axis [au]", value=0.0)
            period = st.number_input("Orbital Period [days]", value=1.0)
            dur = st.number_input("Transit Duration [hrs]", value=1.0)
            steff = st.number_input("Stellar Effective Temperature [K]", value=5600.0)
            depth = st.number_input("Transit Depth [ppm]", value=0.0)
            slogg = st.number_input("Stellar Surface Gravity [log10(cm/s**2)]", value=4.4)
            srad = st.number_input("Stellar Radius [Solar radii]", value=1.0)
            time0bk = st.number_input("Transit Epoch [BKJD]", value=2459000.0)
            submitted = st.form_submit_button("Agregar y predecir")

        if submitted:
            if not name:
                st.warning("Introduce un nombre para el exoplaneta")
            else:
                # preparar features para el modelo (si existe)
                features = [snr, rade, sma, eqt, period, dur, depth, steff, slogg, srad, time0bk]
                pred_label = None
                if model is not None and scaler is not None and encoder is not None:
                    try:
                        Xs = scaler.transform([features])
                        p = model.predict(Xs)
                        pred_label = encoder.inverse_transform(p)[0]
                    except Exception as e:
                        st.error(f"Error al predecir: {e}")

                # Normalizar coords según los rangos actuales en exo_df (si hay datos)
                try:
                    if len(exo_df) > 0 and 'ra' in exo_df.columns and 'dec' in exo_df.columns and exo_df['ra'].notnull().any():
                        x0 = (ra - exo_df['ra'].min()) / (exo_df['ra'].max() - exo_df['ra'].min())
                        y0 = (dec - exo_df['dec'].min()) / (exo_df['dec'].max() - exo_df['dec'].min())
                    else:
                        x0, y0 = 0.5, 0.5
                except Exception:
                    x0, y0 = 0.5, 0.5

                new_row = {
                    'pl_name': name,
                    'hostname': name,
                    'ra': ra,
                    'dec': dec,
                    'pl_rade': rade,
                    'pl_eqt': eqt,
                    'x': x0,
                    'y': y0,
                    'pred_class': pred_label
                }
                exo_df = pd.concat([exo_df, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.exo_df = exo_df
                st.success(f"Exoplaneta '{name}' agregado." + (f" Predicción: {pred_label}" if pred_label is not None else ""))

        st.markdown("---")
        st.subheader("Seleccionar/Información")
        options = exo_df['hostname'].fillna(exo_df['pl_name']).astype(str).tolist()
        selected = st.selectbox("Selecciona un exoplaneta para ver detalles", options=options if options else ["-"])
        if selected and selected != "-":
            row = exo_df[exo_df['hostname'].astype(str) == selected].iloc[-1]
            st.markdown(f"**Nombre:** {row.get('pl_name', '')}")
            st.markdown(f"**Radio:** {row.get('pl_rade', '')} R⊕")
            st.markdown(f"**Temperatura:** {row.get('pl_eqt', '')} K")
            st.markdown(f"**RA, Dec:** {row.get('ra', '')}, {row.get('dec', '')}")
            if pd.notna(row.get('pred_class')):
                st.markdown(f"**Predicción (ML):** {row.get('pred_class')}")
            # Información KOI si existe
            koi_key = str(selected)
            if koi_key in koi_dict:
                k = koi_dict[koi_key]
                st.markdown(f"**KOI disposition:** {k.get('koi_disposition')}")
                st.markdown(f"**KOI prad:** {k.get('koi_prad')}")

    with right:
        st.subheader("Visualización 2D interactiva")
        size_scale = st.sidebar.slider("Escala de tamaño de puntos", 1.0, 50.0, 10.0)

        plot_df = exo_df.copy()
        plot_df['size_plot'] = plot_df['pl_rade'].astype(float).fillna(0.5) * size_scale
        # Marcar seleccionado para agrandar
        if selected and selected != "-":
            plot_df['selected'] = plot_df['hostname'].astype(str) == selected
            # Aumentar tamaño del seleccionado
            plot_df.loc[plot_df['selected'], 'size_plot'] = plot_df.loc[plot_df['selected'], 'size_plot'] * 2.5
        else:
            plot_df['selected'] = False

        try:
            fig = px.scatter(
                plot_df,
                x='x',
                y='y',
                size='size_plot',
                color='pl_eqt' if 'pl_eqt' in plot_df.columns else None,
                hover_name='pl_name',
                hover_data=['hostname', 'pl_rade', 'pl_eqt'],
                title='Distribución 2D de exoplanetas (RA/Dec normalizados)',
                labels={'x': 'RA (normalizado)', 'y': 'Dec (normalizado)'}
            )
            fig.update_layout(height=700)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creando la visualización: {e}")

        st.markdown("---")
        st.subheader("Tabla de exoplanetas")
        st.dataframe(exo_df.reset_index(drop=True))

elif page == "Simulador 3D":
    st.header("Simulador 3D")
    st.write("Visualización 3D interactiva de los exoplanetas. Usa los controles para ajustar tamaño y color.")

    # Preparar datos 3D: usar RA/Dec y otra variable (p.e. distancia o pl_rade) como Z si está disponible
    df3 = st.session_state.get('exo_df', pd.DataFrame()).copy()
    if df3.empty:
        st.info("No hay datos para mostrar en 3D. Asegúrate de tener 'exoplanets_visual.csv' en ML/ o agrega exoplanetas desde el simulador 2D.")
    else:
        # Si no hay columna de distancia, usar pl_rade como Z
        if 'sy_dist' in df3.columns:
            df3['z'] = pd.to_numeric(df3['sy_dist'], errors='coerce').fillna(df3['pl_rade'].astype(float).fillna(0.5))
        else:
            df3['z'] = df3['pl_rade'].astype(float).fillna(0.5)

        z_scale = st.sidebar.slider("Escala Z", 0.1, 10.0, 1.0)
        size_scale_3d = st.sidebar.slider("Escala tamaño 3D", 1.0, 50.0, 8.0)

        try:
            fig3 = px.scatter_3d(
                df3,
                x='x',
                y='y',
                z=df3['z'] * z_scale,
                color='pl_eqt' if 'pl_eqt' in df3.columns else None,
                size=df3['pl_rade'].astype(float).fillna(0.5) * size_scale_3d,
                hover_name='pl_name',
                hover_data=['hostname', 'pl_rade', 'pl_eqt'],
                title='Simulación 3D de exoplanetas'
            )
            fig3.update_layout(height=750)
            st.plotly_chart(fig3, use_container_width=True)
        except Exception as e:
            st.error(f"Error creando la visualización 3D: {e}")

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
