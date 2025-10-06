import streamlit as st
import pandas as pd
import joblib
import os
import requests
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador y Clasificador de Exoplanetas", layout="wide")

# Base dir para cargar assets (style.css)
base_dir = os.path.dirname(__file__)
style_path = os.path.join(base_dir, "style.css")
css = ""
if os.path.exists(style_path):
    try:
        with open(style_path, "r", encoding="utf-8") as f:
            css = f.read()
    except Exception:
        css = ""

if css:
        # Evitar reglas globales que rompan el layout de Streamlit (p.e. overflow: hidden en body)
        css_safe = css
        css_safe = css_safe.replace('body {', '/* body { */')
        css_safe = css_safe.replace('overflow: hidden;', '/* overflow: hidden; */')
        css_safe = css_safe.replace('height: 100vh;', '/* height: 100vh; */')
        # Añadir reglas para ocultar elementos de Streamlit y estilizar botones
        extra = '''
        /* Ocultar barra superior y footer de Streamlit */
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        header {visibility: hidden !important;}
        [data-testid="stToolbar"] {display:none !important;}

        /* Estilo para botones de Streamlit para que coincidan con index.css */
        .stButton>button, button[data-baseweb="button"] {
            background-color: #00bfff !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 10px 16px !important;
            font-weight: 700 !important;
            box-shadow: 0 6px 18px rgba(0,191,255,0.12) !important;
        }
        .stButton>button:hover, button[data-baseweb="button"]:hover { background-color: #0077b3 !important; }

        /* Ajustes del contenedor principal de Streamlit para centrar y dar espacio */
        .app-view-container .main .block-container {
            padding-top: 20px !important;
            padding-left: 20px !important;
            padding-right: 20px !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
            background: transparent !important;
        }
        '''
        st.markdown(f"<style>{css_safe}\n{extra}</style>", unsafe_allow_html=True)

# NOTE: header/hero is rendered dynamically below (depends on selected `page`)

# Páginas disponibles (usa session_state para sincronizar con botones del header)
if 'page' not in st.session_state:
    st.session_state.page = "Simulador 2D"
st.sidebar.header("Navegación")
# Añadimos la página "Asistente" al menú de opciones para acceder al asistente virtual
page = st.sidebar.selectbox("Selecciona una sección:", ["Simulador 2D", "Simulador 3D", "Clasificador ML", "Asistente"], key='page')

# Header quick buttons removed — la navegación ahora se gestiona únicamente desde el menú lateral
# (mantener la variable `page` sincronizada con session_state)
page = st.session_state.page

# Dynamic hero: show intro cover or simulator preview depending on selected page
def render_hero(page_selected: str):
    intro_html = '''
    <div class="hero" style="display:flex;align-items:center;justify-content:center;flex-direction:column;padding:40px 10px;margin-bottom:20px;">
        <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='900' height='240'><rect width='100%' height='100%' fill='%23010a12'/><text x='50%' y='40%' fill='%2300bfff' font-family='Orbitron, sans-serif' font-size='40' text-anchor='middle'>Exoplanet Explorer</text><text x='50%' y='70%' fill='%23ffffff' font-family='Arial' font-size='18' text-anchor='middle'>Simulador y Clasificador de Exoplanetas</text></svg>" style="max-width:100%;border-radius:12px;box-shadow:0 14px 40px rgba(0,0,0,0.5);"/>
    </div>
    '''

    sim2d_html = '''
    <div class="hero" style="display:flex;align-items:center;justify-content:center;flex-direction:column;padding:20px;margin-bottom:20px;">
        <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='900' height='240'><rect width='100%' height='100%' fill='%2300101a'/><text x='50%' y='50%' fill='%237ec8ff' font-family='Orbitron, sans-serif' font-size='30' text-anchor='middle'>Simulador 2D - Vista previa</text></svg>" style="max-width:100%;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,0.45);"/>
    </div>
    '''

    sim3d_html = '''
    <div class="hero" style="display:flex;align-items:center;justify-content:center;flex-direction:column;padding:20px;margin-bottom:20px;">
        <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='900' height='240'><rect width='100%' height='100%' fill='%23000a14'/><text x='50%' y='50%' fill='%23a4d4ff' font-family='Orbitron, sans-serif' font-size='30' text-anchor='middle'>Simulador 3D - Vista previa</text></svg>" style="max-width:100%;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,0.45);"/>
    </div>
    '''

    if page_selected == 'Simulador 2D':
        st.markdown(sim2d_html, unsafe_allow_html=True)
    elif page_selected == 'Simulador 3D':
        st.markdown(sim3d_html, unsafe_allow_html=True)
    else:
        st.markdown(intro_html, unsafe_allow_html=True)

render_hero(page)

# Render simple chat widget HTML (uses CSS from style.css) but only show it on the main menu ('Clasificador ML')
chat_html = '''
<div class="chat-widget" id="chatWidget">
    <div class="chat-header" onclick="toggleChat()">
        Asistente 🤖
        <span id="chatToggleIcon">▼</span>
    </div>
    <div class="chat-body" id="chatBody">
        <div class="chat-messages" id="chatMessages">
        </div>
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="Escribe una pregunta...">
            <button onclick="sendMessage()">➤</button>
        </div>
    </div>
</div>

<script>
function toggleChat(){
    const b=document.getElementById('chatBody');
    const ic=document.getElementById('chatToggleIcon');
    if(b.style.display==='flex'){b.style.display='none';ic.style.transform='rotate(0deg)';}
    else{b.style.display='flex';ic.style.transform='rotate(180deg)';}
}
async function sendMessage(){
    const input=document.getElementById('userInput');
    const text=input.value.trim(); if(!text) return;
    const msgs=document.getElementById('chatMessages');
    const um=document.createElement('div'); um.className='user-message'; um.textContent=text; msgs.appendChild(um);
    input.value=''; msgs.scrollTop=msgs.scrollHeight;
    try{
        const resp=await fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:text})});
        const data=await resp.json();
        const bm=document.createElement('div'); bm.className='bot-message'; bm.textContent=data.response||data.error||'No hay respuesta'; msgs.appendChild(bm);
    }catch(e){
        const bm=document.createElement('div'); bm.className='bot-message'; bm.textContent='Asistente: '+(e.message||'Error en la conexión'); msgs.appendChild(bm);
    }
    msgs.scrollTop=msgs.scrollHeight;
}
</script>
'''

# Only inject the floating chat widget on the dedicated 'Asistente' page
if page == "Asistente":
    st.components.v1.html(chat_html, height=420)

# --- Asistente virtual para usuarios noveles (barra lateral) ---
if 'assistant_messages' not in st.session_state:
    st.session_state.assistant_messages = [
        ("bot", "Hola 👋, soy el asistente. Puedo ayudarte a usar el simulador 2D/3D y el clasificador. Pregunta cosas como: '¿Cómo cargo datos?' o '¿Cómo agrego un exoplaneta?'.")
    ]

def generate_fallback_reply(user_text: str) -> str:
    t = user_text.lower()
    # Preguntas sobre exoplanetas (español)
    if 'exoplanet' in t or 'exoplaneta' in t or 'qué es un exoplaneta' in t or 'que es un exoplaneta' in t:
        return (
            "Un exoplaneta (o planeta extrasolar) es un planeta que orbita una estrella fuera del Sistema Solar. "
            "Se detectan principalmente por el método del tránsito (cuando el planeta pasa frente a su estrella y produce una pequeña disminución del brillo), "
            "por velocidades radiales (variaciones en la velocidad de la estrella debidas a la gravedad del planeta), y por imágenes directas o microlente gravitatoria. "
            "Los exoplanetas pueden variar mucho en tamaño y temperatura: desde gigantes gaseosos más grandes que Júpiter hasta planetas rocosos más pequeños que la Tierra. "
            "Si quieres, puedo explicarte con más detalle los métodos de detección o cómo interpretar las columnas del CSV de ejemplo."
        )
    if '3d' in t or '3 d' in t:
        return "Para usar el simulador 3D: ve a 'Simulador 3D' desde el menú y usa los controles para ajustar la escala y colores. Si no ves puntos, comprueba que el CSV 'ML/exoplanets_visual.csv' existe."
    if '2d' in t:
        return "En 'Simulador 2D' puedes ver la distribución en RA/Dec. Usa el formulario para agregar un exoplaneta y el botón de predicción si tienes los modelos en la carpeta ML/."
    if 'csv' in t or 'datos' in t:
        return "El archivo de datos esperado está en 'Pagina_web_en_24/ML/exoplanets_visual.csv'. Si no existe, copia el CSV allí o actualiza la ruta en el código."
    if 'modelo' in t or 'model' in t or 'predict' in t:
        return "Para habilitar predicciones ML debes tener 'exoplanet_classifier.joblib', 'scaler.joblib' y 'label_encoder.joblib' en la carpeta ML/. Si no están, el formulario seguirá permitiendo añadir exoplanetas pero sin predicción."
    return "Puedo ayudarte con: cómo usar los simuladores 2D/3D, cómo añadir exoplanetas, o cómo preparar los archivos ML. Fórmulate una pregunta concreta o escribe 'ayuda'."

if page == "Asistente":
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
            # No forzamos rerun; Streamlit mostrará los nuevos mensajes en la próxima interacción

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
    st.header("Simulador 3D — Proyecto NASA")
    st.write("Visualización 3D interactiva de los exoplanetas. Basado en el proyecto NASA diseñado en la carpeta 'proyecto nasa'.")

    # Constantes de conversión
    PC_TO_LY = 3.26156
    PC_TO_AU = 206264.8
    DAY_TO_YEAR = 1 / 365.25
    CAMERA_INITIAL_DISTANCE = 1500.0
    CAMERA_SEARCH_ZOOM_FACTOR = 0.05
    RANGO_MAX_FIJO_PC = 3000.0

    # Cargar datos: preferir st.session_state.exo_df si existe, si no intentar leer el CSV del proyecto
    df3 = st.session_state.get('exo_df', pd.DataFrame()).copy()
    if df3.empty:
        project_csv = os.path.join(base_dir, 'proyecto nasa', 'exoplanets_visual.csv')
        fallback_csv = os.path.join(base_dir, 'ML', 'exoplanets_visual.csv')
        if os.path.exists(project_csv):
            try:
                df3 = pd.read_csv(project_csv)
            except Exception:
                df3 = pd.DataFrame()
        elif os.path.exists(fallback_csv):
            try:
                df3 = pd.read_csv(fallback_csv)
            except Exception:
                df3 = pd.DataFrame()

    if df3.empty:
        st.info("No hay datos para mostrar en 3D. Coloca 'exoplanets_visual.csv' en 'proyecto nasa/' o en 'ML/' o añade exoplanetas desde el simulador 2D.")
    else:
        # Cargar modelos ML si están disponibles (misma lógica que en otras pestañas)
        model3, scaler3, encoder3 = None, None, None
        try:
            model3 = joblib.load(os.path.join(base_dir, "ML", "exoplanet_classifier.joblib"))
            scaler3 = joblib.load(os.path.join(base_dir, "ML", "scaler.joblib"))
            encoder3 = joblib.load(os.path.join(base_dir, "ML", "label_encoder.joblib"))
        except Exception:
            model3 = scaler3 = encoder3 = None

        # Organizar UI al estilo Simulador 2D: dos columnas (controles a la izquierda, visualización a la derecha)
        left, right = st.columns([1, 2])

        with left:
            st.subheader("Controles & Clasificador ML")
            color_mode = st.selectbox("Colorear por:", options=['Temperatura', 'Clasificación ML'])

            # Predicción por lote si es posible
            required_features = ['koi_model_snr', 'koi_prad', 'koi_sma', 'koi_teq', 'koi_period', 'koi_duration', 'koi_depth', 'koi_steff', 'koi_slogg', 'koi_srad', 'koi_time0bk']
            can_batch_predict = model3 is not None and scaler3 is not None and encoder3 is not None and all(feat in df3.columns for feat in required_features)
            if can_batch_predict:
                if st.button("Predecir clasificación ML para todo el dataset"):
                    try:
                        X_batch = df3[required_features].fillna(0).astype(float).values
                        Xs_batch = scaler3.transform(X_batch)
                        preds = model3.predict(Xs_batch)
                        df3['pred_class'] = encoder3.inverse_transform(preds)
                        # Persist results back to session state so the plotting code uses the updated dataframe
                        st.session_state['exo_df'] = df3
                        st.success("Predicción por lote completada: columna 'pred_class' añadida al dataset.")
                        # Rerun to force the UI/plot to refresh with the new 'pred_class' column
                        try:
                            st.experimental_rerun()
                        except Exception:
                            # In some testing environments rerun may raise; it's safe to continue without crashing
                            pass
                    except Exception as e:
                        st.error(f"Error en predicción por lote: {e}")
            else:
                if model3 is None:
                    st.info("Modelo ML no encontrado en ML/. Coloca exoplanet_classifier.joblib, scaler.joblib y label_encoder.joblib en la carpeta ML/.")
                else:
                    st.info("Dataset no contiene las features necesarias para predicción por lote. Puedes usar el formulario individual para predecir un punto.")

            st.markdown("---")
            st.subheader("Predecir y agregar (individual)")
            with st.form("ml_3d_form_left"):
                st.markdown("Introduce las 11 features para predecir la clase del exoplaneta:")
                koi_model_snr_3 = st.number_input("Transit SNR", value=18.0, key='snr_3_left')
                koi_prad_3 = st.number_input("Planetary Radius (koi_prad)", value=0.59, key='prad_3_left')
                koi_sma_3 = st.number_input("Orbit SMA (koi_sma)", value=0.0739, key='sma_3_left')
                koi_teq_3 = st.number_input("Equilibrium Temp (koi_teq)", value=443.0, key='teq_3_left')
                koi_period_3 = st.number_input("Orbital Period (koi_period)", value=10.3128, key='period_3_left')
                koi_duration_3 = st.number_input("Transit Duration (koi_duration)", value=3.2, key='duration_3_left')
                koi_depth_3 = st.number_input("Transit Depth (koi_depth)", value=0.45, key='depth_3_left')
                koi_steff_3 = st.number_input("Stellar Teff (koi_steff)", value=5600.0, key='steff_3_left')
                koi_slogg_3 = st.number_input("Stellar logg (koi_slogg)", value=4.4, key='slogg_3_left')
                koi_srad_3 = st.number_input("Stellar Radius (koi_srad)", value=0.98, key='srad_3_left')
                koi_time0bk_3 = st.number_input("Transit Epoch (koi_time0bk)", value=2459000.123, key='time0bk_3_left')
                add_to_plot = st.checkbox("Agregar punto al plot 3D con la predicción", value=False)
                ml_submitted = st.form_submit_button("Predecir clase (ML)")

            if ml_submitted:
                if model3 is None or scaler3 is None or encoder3 is None:
                    st.error("Modelo ML no encontrado en ML/. Coloca exoplanet_classifier.joblib, scaler.joblib y label_encoder.joblib en la carpeta ML/.")
                else:
                    features3 = [[
                        koi_model_snr_3, koi_prad_3, koi_sma_3, koi_teq_3, koi_period_3,
                        koi_duration_3, koi_depth_3, koi_steff_3, koi_slogg_3, koi_srad_3, koi_time0bk_3
                    ]]
                    try:
                        Xs3 = scaler3.transform(features3)
                        p3 = model3.predict(Xs3)
                        pred_label3 = encoder3.inverse_transform(p3)[0]
                        st.success(f"Predicción ML: {pred_label3}")
                        if add_to_plot:
                            new_name = f"ML_added_{len(st.session_state.exo_df) + 1}"
                            new_row = {
                                'pl_name': new_name,
                                'hostname': new_name,
                                'ra': 0.0,
                                'dec': 0.0,
                                'pl_rade': koi_prad_3,
                                'pl_eqt': koi_teq_3,
                                'x': 0.5,
                                'y': 0.5,
                                'pred_class': pred_label3
                            }
                            st.session_state.exo_df = pd.concat([st.session_state.exo_df, pd.DataFrame([new_row])], ignore_index=True)
                            st.info(f"Punto agregado: {new_name}")
                    except Exception as e:
                        st.error(f"Error en predicción ML: {e}")

            st.markdown("---")
            st.subheader("Seleccionar/Información")
            options3 = df3['hostname'].fillna(df3['pl_name']).astype(str).tolist()
            selected3 = st.selectbox("Selecciona un exoplaneta para ver detalles", options=options3 if options3 else ["-"])
            if selected3 and selected3 != "-":
                row3 = df3[df3['hostname'].astype(str) == selected3].iloc[-1]
                st.markdown(f"**Nombre:** {row3.get('pl_name', '')}")
                st.markdown(f"**Radio:** {row3.get('pl_rade', '')} R⊕")
                st.markdown(f"**Temperatura:** {row3.get('pl_eqt', '')} K")
                st.markdown(f"**RA, Dec:** {row3.get('ra', '')}, {row3.get('dec', '')}")
                if pd.notna(row3.get('pred_class')):
                    st.markdown(f"**Predicción (ML):** {row3.get('pred_class')}")

        with right:
            # Aquí se renderiza la figura 3D (reutiliza el código de construcción de la figura más abajo)
            st.subheader("Visualización 3D interactiva")
            # escala de tamaño similar al 2D
            size_scale_3d = st.slider("Escala de tamaño de puntos (3D)", 1.0, 50.0, 8.0)
            # preparar tamaños de marker
            df3['size_plot'] = df3['pl_rade'].astype(float).fillna(0.5) * size_scale_3d

            # Marcar seleccionado para agrandar
            if 'selected3' in locals() and selected3 and selected3 != "-":
                df3['selected'] = df3['hostname'].astype(str) == selected3
                df3.loc[df3['selected'], 'size_plot'] = df3.loc[df3['selected'], 'size_plot'] * 2.5
            else:
                df3['selected'] = False

            # el plotting se realiza más abajo usando df3 y fig_data_highlight
        # Asegurar columnas y tipos
        for col in ['ra', 'dec', 'sy_dist', 'st_teff', 'pl_name', 'pl_orbper', 'pl_eqt']:
            if col not in df3.columns:
                df3[col] = np.nan
        for col in ['ra', 'dec', 'sy_dist', 'st_teff', 'pl_orbper', 'pl_eqt']:
            df3[col] = pd.to_numeric(df3[col], errors='coerce')

        # Filtrado suave similar al proyecto
        df3 = df3.dropna(subset=['ra', 'dec', 'sy_dist', 'pl_name'])
        df3 = df3[df3['sy_dist'] > 0.01]
        df3 = df3[(df3['ra'] >= 0) & (df3['ra'] <= 360)]
        df3 = df3[(df3['dec'] >= -90) & (df3['dec'] <= 90)]
        df3 = df3[(df3['st_teff'] >= 1000) & (df3['st_teff'] <= 10000)]

        # Unidades y controles
        st.sidebar.subheader("Controles - Proyecto NASA")
        unit = st.sidebar.selectbox("Unidades", options=['pc', 'ly', 'au'], index=0)
        planet_options = sorted(df3['pl_name'].dropna().unique().tolist())
        planet_sel = st.sidebar.selectbox("Buscar exoplaneta por nombre", options=['(ninguno)'] + planet_options)
        unit_name = 'pc'
        if unit == 'pc':
            dist_col = 'sy_dist'
            unit_name = 'pc'
            factor_conversion = 1.0
        elif unit == 'ly':
            dist_col = 'sy_dist_ly' if 'sy_dist_ly' in df3.columns else 'sy_dist'
            unit_name = 'al'
            factor_conversion = PC_TO_LY
            if 'sy_dist_ly' not in df3.columns:
                df3['sy_dist_ly'] = df3['sy_dist'] * PC_TO_LY
        else:
            dist_col = 'sy_dist_au' if 'sy_dist_au' in df3.columns else 'sy_dist'
            unit_name = 'UA'
            factor_conversion = PC_TO_AU
            if 'sy_dist_au' not in df3.columns:
                df3['sy_dist_au'] = df3['sy_dist'] * PC_TO_AU

        # Convertir a radianes
        df3['ra_rad'] = np.deg2rad(df3['ra'])
        df3['dec_rad'] = np.deg2rad(df3['dec'])

        # Calcular coordenadas 3D
        df3['x'] = df3[dist_col] * np.cos(df3['dec_rad']) * np.cos(df3['ra_rad'])
        df3['y'] = df3[dist_col] * np.cos(df3['dec_rad']) * np.sin(df3['ra_rad'])
        df3['z'] = df3[dist_col] * np.sin(df3['dec_rad'])

        # Rango dinámico
        RANGO_MAX_DINAMICO = RANGO_MAX_FIJO_PC * factor_conversion
        RANGO_FIJO_DINAMICO = [-RANGO_MAX_DINAMICO, RANGO_MAX_DINAMICO]

        # Colores por temp
        temp_min_planet = df3['pl_eqt'].min()
        temp_max_planet = df3['pl_eqt'].max()
        if temp_min_planet == temp_max_planet or pd.isna(temp_min_planet) or pd.isna(temp_max_planet):
            temp_min_planet = 100
            temp_max_planet = 3000

        # Cámara por defecto
        INITIAL_DIST_ADJUSTED = CAMERA_INITIAL_DISTANCE * factor_conversion
        default_camera = dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=INITIAL_DIST_ADJUSTED, y=INITIAL_DIST_ADJUSTED, z=INITIAL_DIST_ADJUSTED)
        )

        final_camera = default_camera
        search_message = ""
        fig_data_highlight = []

        # Si se seleccionó un planeta, centrar y resaltar
        if planet_sel and planet_sel != '(ninguno)':
            sel_row = df3[df3['pl_name'] == planet_sel]
            if not sel_row.empty:
                x_t = sel_row['x'].iloc[0]
                y_t = sel_row['y'].iloc[0]
                z_t = sel_row['z'].iloc[0]
                distancia_muestra = sel_row[dist_col].iloc[0]

                MAX_FOR_ZOOM = RANGO_MAX_DINAMICO
                zoom_dist_search = MAX_FOR_ZOOM * CAMERA_SEARCH_ZOOM_FACTOR
                zoom_camera = dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=x_t, y=y_t, z=z_t),
                    eye=dict(x=x_t + zoom_dist_search, y=y_t + zoom_dist_search, z=z_t + zoom_dist_search)
                )
                final_camera = zoom_camera

                # estado confirmado/candidato heurístico
                if planet_sel.split(' ')[-1].isalpha() and not planet_sel.endswith('.01'):
                    estado = "CONFIRMADO ✅"
                else:
                    estado = "CANDIDATO ⚠️"

                temp_eqt_val = sel_row['pl_eqt'].iloc[0]
                temp_display = f"{temp_eqt_val:.0f} K" if not pd.isna(temp_eqt_val) else "N/D"

                search_message = f"Estado: {estado} | Planeta: {planet_sel} | Distancia: {distancia_muestra:.2f} {unit_name} | T° Planeta: {temp_display}."

                fig_data_highlight = [
                    go.Scatter3d(
                        x=[x_t], y=[y_t], z=[z_t], mode='markers',
                        marker=dict(size=12, color='#00BFFF', symbol='circle', line=dict(width=2, color='white')),
                        name=planet_sel, hoverinfo='text',
                        text=[f"🌟 ¡OBJETO BUSCADO!<br>{planet_sel}<br>Dist: {distancia_muestra:.2f} {unit_name}<br>T: {temp_display}"],
                        showlegend=False
                    )
                ]
            else:
                search_message = f"⚠️ Planeta '{planet_sel}' no encontrado en el dataset actual."

        # Construir figura
        # Preparar textos de hover fuera de la lista de datos para evitar sintaxis inválida
        per_series = df3.get('pl_orbper', pd.Series([np.nan] * len(df3)))
        hover_texts = []
        for n, d, t, p in zip(df3['pl_name'], df3[dist_col], df3['pl_eqt'], per_series):
            if pd.isna(t):
                hover_texts.append(f"Nombre: {n}<br>T° Planeta: N/D<br>Distancia: {d:.2f} {unit_name}")
            else:
                # convertir periodo a años si es posible
                try:
                    per_yr = float(p) * DAY_TO_YEAR if (not pd.isna(p)) else None
                except Exception:
                    per_yr = None
                if per_yr is not None and not pd.isna(per_yr):
                    hover_texts.append(f"Nombre: {n}<br>T° Planeta: {t:.0f} K<br>Distancia: {d:.2f} {unit_name}<br>Período: {per_yr:.2f} años")
                else:
                    hover_texts.append(f"Nombre: {n}<br>T° Planeta: {t:.0f} K<br>Distancia: {d:.2f} {unit_name}")

        # Preparar data y color según modo
        if color_mode == 'Clasificación ML' and 'pred_class' in df3.columns:
            color_col = 'pred_class'
            # Map categories to colors via Plotly's categorical coloring
            marker_dict = dict(size=4, opacity=0.9, line=dict(width=0.2, color='white'))
        else:
            color_col = 'pl_eqt'
            marker_dict = dict(size=4, color=df3['pl_eqt'], colorscale='Plasma', cmin=temp_min_planet, cmax=temp_max_planet,
                                colorbar=dict(title='Temp. Planeta (K)', thickness=20), opacity=0.8, line=dict(width=0.2, color='white'))

        # Crear scatter3d para los exoplanetas; si es categórico, crear una traza por categoría para la leyenda
        # Ajustar tamaños relativos según el radio (mejor visibilidad)
        sizes = (df3['pl_rade'].astype(float).fillna(0.5) - df3['pl_rade'].astype(float).fillna(0.5).min())
        if sizes.max() > 0:
            sizes = 6 + 18 * (sizes / sizes.max())
        else:
            sizes = np.full(len(df3), 6)

        hovertemplate = "%{text}<extra></extra>"

        traces = []
        # Add a soft starfield in the background for depth (few hundred faint points)
        try:
            rng = np.random.default_rng(42)
            n_stars = 300
            star_x = rng.uniform(RANGO_FIJO_DINAMICO[0]*0.9, RANGO_FIJO_DINAMICO[1]*0.9, n_stars)
            star_y = rng.uniform(RANGO_FIJO_DINAMICO[0]*0.9, RANGO_FIJO_DINAMICO[1]*0.9, n_stars)
            star_z = rng.uniform(RANGO_FIJO_DINAMICO[0]*0.9, RANGO_FIJO_DINAMICO[1]*0.9, n_stars)
            star_trace = go.Scatter3d(x=star_x, y=star_y, z=star_z, mode='markers',
                                      marker=dict(size=1.5, color='white', opacity=0.15),
                                      hoverinfo='none', showlegend=False)
            traces.append(star_trace)
        except Exception:
            pass

        if color_col == 'pred_class' and 'pred_class' in df3.columns:
            categories = sorted(df3['pred_class'].dropna().unique().tolist())
            color_list = px.colors.qualitative.Plotly
            color_map = {cat: color_list[i % len(color_list)] for i, cat in enumerate(categories)}
            for cat in categories:
                mask = df3['pred_class'] == cat
                if mask.sum() == 0:
                    continue
                traces.append(go.Scatter3d(
                    x=df3.loc[mask, 'x'], y=df3.loc[mask, 'y'], z=df3.loc[mask, 'z'], mode='markers',
                    marker=dict(size=sizes[mask.index[mask].tolist()] if hasattr(sizes, 'index') else sizes[mask], color=color_map.get(cat), opacity=0.95, line=dict(width=0.3, color='white')),
                    name=str(cat), text=[hover_texts[i] for i in range(len(df3)) if mask.iloc[i]], hovertemplate=hovertemplate, hoverinfo='text'
                ))
        else:
            # Continuous temperature coloring
            traces.append(go.Scatter3d(x=df3['x'], y=df3['y'], z=df3['z'], mode='markers',
                                       marker=dict(size=sizes, color=df3['pl_eqt'], colorscale='Plasma', cmin=temp_min_planet, cmax=temp_max_planet,
                                                   colorbar=dict(title='Temp. Planeta (K)', thickness=20), opacity=0.85, line=dict(width=0.2, color='white')),
                                       name='Exoplanetas', text=hover_texts, hovertemplate=hovertemplate, hoverinfo='text'))

        # Sistema Solar punto central
        traces.insert(len(traces), go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', marker=dict(size=10, color='gold', symbol='diamond', line=dict(width=1, color='white')), name='Sistema Solar', hoverinfo='text', text=["Sistema Solar (Tierra)"]))

        # Añadir highlight si aplica
        traces = traces + fig_data_highlight

        fig = go.Figure(data=traces)
        fig.update_layout(
            title=f"Exoplanetas en 3D (en {unit_name})",
            scene=dict(
                xaxis=dict(range=RANGO_FIJO_DINAMICO, backgroundcolor="#000010", gridcolor="#222222", zerolinecolor="#333333", title=f'X ({unit_name})'),
                yaxis=dict(range=RANGO_FIJO_DINAMICO, backgroundcolor="#000010", gridcolor="#222222", zerolinecolor="#333333", title=f'Y ({unit_name})'),
                zaxis=dict(range=RANGO_FIJO_DINAMICO, backgroundcolor="#000010", gridcolor="#222222", zerolinecolor="#333333", title=f'Z ({unit_name})'),
                aspectmode='cube',
                camera=final_camera,
                uirevision=planet_sel if planet_sel else 'PersistentView'
            ),
            height=820, paper_bgcolor="#070712", plot_bgcolor="#070712", font=dict(color='white'), margin=dict(l=0, r=0, t=50, b=0),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )

        # Mejoras al hoverlabel
        fig.update_traces(hoverlabel=dict(bgcolor="#111111", font_color='white'))

        st.plotly_chart(fig, use_container_width=True)
        if search_message:
            st.markdown(f"**{search_message}**")

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
