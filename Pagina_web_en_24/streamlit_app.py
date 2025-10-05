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

# Visual header similar to index.html
st.markdown(
        """
        <div class="stars" style="z-index:-1;"></div>
        <div class="container" style="margin-bottom:20px;">
            <h1>Exoplanet Explorer</h1>
            <section class="intro">
                <h2>Simulador y Clasificador</h2>
                <p>Visualiza y explora exoplanetas con simuladores 2D y 3D. Añade objetos y usa el clasificador ML si tienes los modelos.</p>
            </section>
        </div>
        """,
        unsafe_allow_html=True,
)

# Páginas disponibles (usa session_state para sincronizar con botones del header)
if 'page' not in st.session_state:
    st.session_state.page = "Simulador 2D"
st.sidebar.header("Navegación")
page = st.sidebar.selectbox("Selecciona una sección:", ["Simulador 2D", "Simulador 3D", "Clasificador ML"], key='page')

# Header quick buttons (visually similar to index.html)
col1, col2, col3 = st.columns([1,1,6])
with col1:
    if st.button("Abrir Modelo 2D"):
        st.session_state.page = "Simulador 2D"
with col2:
    if st.button("Abrir Modelo 3D"):
        st.session_state.page = "Simulador 3D"
with col3:
    # placeholder for spacing/title already shown in the big container
    st.write("")

# Asegurar que 'page' refleja botones del header
page = st.session_state.page

# Render simple chat widget HTML (uses CSS from style.css)
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
    // Add user message to local DOM
    const msgs=document.getElementById('chatMessages');
    const um=document.createElement('div'); um.className='user-message'; um.textContent=text; msgs.appendChild(um);
    input.value=''; msgs.scrollTop=msgs.scrollHeight;
    // Call backend (Streamlit assistant via sidebar form will also keep history);
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
    st.write("Visualización 3D interactiva de los exoplanetas con estilo 'Proyecto NASA'. Usa los controles para ajustar filtros, escalas y animación de cámara.")

    # Preparar datos 3D: usar RA/Dec y otra variable (p.e. distancia o pl_rade) como Z si está disponible
    df3 = st.session_state.get('exo_df', pd.DataFrame()).copy()
    if df3.empty:
        st.info("No hay datos para mostrar en 3D. Asegúrate de tener 'exoplanets_visual.csv' en ML/ o agrega exoplanetas desde el simulador 2D.")
    else:
        # Z preferente: sy_dist, si no pl_rade
        if 'sy_dist' in df3.columns:
            df3['z'] = pd.to_numeric(df3['sy_dist'], errors='coerce').fillna(df3['pl_rade'].astype(float).fillna(0.5))
        else:
            df3['z'] = df3['pl_rade'].astype(float).fillna(0.5)

        # filtros y controles estilo proyecto
        st.sidebar.subheader("Controles - Proyecto NASA")
        methods = ['(todos)']
        if 'discoverymethod' in df3.columns:
            methods = ['(todos)'] + sorted(df3['discoverymethod'].dropna().unique().tolist())
        sel_method = st.sidebar.selectbox("Filtrar por método de descubrimiento", methods)
        year_min, year_max = None, None
        if 'disc_year' in df3.columns:
            try:
                years = pd.to_numeric(df3['disc_year'], errors='coerce').dropna().astype(int)
                if not years.empty:
                    year_min = int(years.min())
                    year_max = int(years.max())
                    sel_year = st.sidebar.slider("Filtrar por año de descubrimiento", year_min, year_max, (year_min, year_max))
                else:
                    sel_year = None
            except Exception:
                sel_year = None
        else:
            sel_year = None

        z_scale = st.sidebar.slider("Escala Z", 0.1, 10.0, 1.0)
        size_scale_3d = st.sidebar.slider("Escala tamaño 3D", 1.0, 80.0, 12.0)
        rotate_auto = st.sidebar.checkbox("Animar rotación de cámara", value=False)

        plot_df = df3.copy()
        # aplicar filtros
        if sel_method and sel_method != '(todos)':
            plot_df = plot_df[plot_df['discoverymethod'] == sel_method]
        if sel_year is not None:
            plot_df = plot_df[(pd.to_numeric(plot_df.get('disc_year'), errors='coerce') >= sel_year[0]) & (pd.to_numeric(plot_df.get('disc_year'), errors='coerce') <= sel_year[1])]

        if plot_df.empty:
            st.warning("No hay objetos que cumplan los filtros seleccionados.")
        else:
            # preparar valores para plot
            xs = plot_df['x'].astype(float).tolist()
            ys = plot_df['y'].astype(float).tolist()
            zs = (plot_df['z'].astype(float) * z_scale).tolist()
            names = plot_df.get('pl_name', plot_df.get('hostname', pd.Series(['']*len(plot_df)))).astype(str).tolist()
            temps = plot_df['pl_eqt'].astype(float).fillna(0).tolist() if 'pl_eqt' in plot_df.columns else [0]*len(plot_df)
            sizes = plot_df['pl_rade'].astype(float).fillna(0.5).tolist()
            sizes_plot = [max(2, s) * (size_scale_3d/4.0) for s in sizes]

            # crear figura con go para mayor control
            scatter = go.Scatter3d(
                x=xs, y=ys, z=zs,
                mode='markers',
                marker=dict(
                    size=sizes_plot,
                    color=temps,
                    colorscale='Turbo',
                    colorbar=dict(title='Temp [K]'),
                    opacity=0.9,
                    line=dict(width=0)
                ),
                hovertemplate='<b>%{text}</b><br>RA: %{x:.3f}<br>Dec: %{y:.3f}<br>Z: %{z:.3f}<extra></extra>',
                text=names
            )

            # layout estilo NASA
            camera = dict(eye=dict(x=1.6, y=1.6, z=0.9))
            layout = go.Layout(
                title=dict(text='Proyecto NASA — Simulación 3D de Exoplanetas', x=0.5, xanchor='center'),
                scene=dict(
                    bgcolor='black',
                    xaxis=dict(title='RA (normalizado)', showgrid=False, zeroline=False, showticklabels=True, color='white'),
                    yaxis=dict(title='Dec (normalizado)', showgrid=False, zeroline=False, showticklabels=True, color='white'),
                    zaxis=dict(title='Z (dist / R)', showgrid=False, zeroline=False, showticklabels=True, color='white')
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=60, b=0),
                scene_camera=camera,
                height=780
            )

            fig3 = go.Figure(data=[scatter], layout=layout)

            # si rotación automática está activada, generar frames para girar la cámara
            if rotate_auto:
                frames = []
                n_frames = 36
                radius = 1.8
                for i, ang in enumerate(np.linspace(0, 2*np.pi, n_frames)):
                    eye = dict(x=radius*np.cos(ang), y=radius*np.sin(ang), z=0.9)
                    frames.append(go.Frame(name=str(i), layout=dict(scene_camera=dict(eye=eye))))
                fig3.frames = frames
                fig3.update_layout(
                    updatemenus=[dict(type='buttons', showactive=False,
                                      y=1, x=1.1, xanchor='right', yanchor='top',
                                      buttons=[dict(label='Play', method='animate', args=[None, dict(frame=dict(duration=80, redraw=True), fromcurrent=True, transition=dict(duration=0))])])]
                )

            # mostrar figura
            st.plotly_chart(fig3, use_container_width=True)

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
