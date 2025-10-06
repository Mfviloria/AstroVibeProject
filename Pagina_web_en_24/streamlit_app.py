import streamlit as st
import pandas as pd
import joblib
import os
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Exoplanet Simulator and Classifier", layout="wide")

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
    css_safe = css_safe.replace("body {", "/* body { */")
    css_safe = css_safe.replace("overflow: hidden;", "/* overflow: hidden; */")
    css_safe = css_safe.replace("height: 100vh;", "/* height: 100vh; */")
    # Añadir reglas para ocultar elementos de Streamlit y estilizar botones
    extra = """
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

        /* Ajustes del contenedor principal de Streamlit para usar todo el ancho */
        /* Broad overrides to ensure main app content can use full width */
        [data-testid="stAppViewContainer"] ,
        .app-view-container,
        .reportview-container,
        .main,
        .block-container,
        .block-container .stApp {
            max-width: 100% !important;
            width: 100% !important;
            margin: 0 !important;
            padding-left: 12px !important;
            padding-right: 12px !important;
            background: transparent !important;
        }

        /* Leave a modest fixed sidebar width so main can expand fully */
        [data-testid="stSidebar"],
        [role="complementary"] {
            width: 300px !important;
            min-width: 300px !important;
            max-width: 300px !important;
        }

        /* Fallback selectors for older/newer Streamlit versions */
        .css-1d391kg .css-1outpf7 { width: calc(100% - 320px) !important; }

        /* Ensure plotly charts and dataframes expand to container width */
        .stPlotlyChart > div, .stPlotlyChart > div > div, .element-container .stPlotlyChart {
            width: 100% !important;
        }
        .stDataFrame, .stDataFrame > div {
            width: 100% !important;
        }

        /* Make the sidebar fixed on the left and shift the main content to the right */
        [data-testid="stSidebar"] {
            position: fixed !important;
            left: 0 !important;
            top: 0 !important;
            height: 100vh !important;
            overflow: auto !important;
            z-index: 999 !important;
        }

        /* Shift the main block container right so it doesn't get overlapped by the fixed sidebar */
        .app-view-container .main .block-container,
        [data-testid="stAppViewContainer"] .main .block-container,
        .reportview-container .main .block-container,
        .block-container {
            margin-left: 320px !important;
            width: calc(100% - 320px) !important;
        }

        /* Ensure widgets inside main expand correctly */
        .stContainer, .main > .block-container > div {
            width: 100% !important;
        }
        """
    st.markdown(f"<style>{css_safe}\n{extra}</style>", unsafe_allow_html=True)

# NOTE: header/hero is rendered dynamically below (depends on selected `page`)

# Páginas disponibles (usa session_state para sincronizar con botones del header)
if "page" not in st.session_state:
    st.session_state.page = "2D Simulator"
st.sidebar.header("Navigation")
page = st.sidebar.selectbox(
    "Select a section:",
    ["2D Simulator", "3D Simulator", "ML Classifier"],
    key="page",
)

# Header quick buttons removed — la navegación ahora se gestiona únicamente desde el menú lateral
# (mantener la variable `page` sincronizada con session_state)
page = st.session_state.page


# Dynamic hero: show intro cover or simulator preview depending on selected page
def render_hero(page_selected: str):
    intro_html = """
    <div class="hero" style="display:flex;align-items:center;justify-content:center;flex-direction:column;padding:40px 10px;margin-bottom:20px;">
        <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='900' height='240'><rect width='100%' height='100%' fill='%23010a12'/><text x='50%' y='40%' fill='%2300bfff' font-family='Orbitron, sans-serif' font-size='40' text-anchor='middle'>Exoplanet Explorer</text><text x='50%' y='70%' fill='%23ffffff' font-family='Arial' font-size='18' text-anchor='middle'>Exoplanet Simulator and Classifier</text></svg>" style="max-width:100%;border-radius:12px;box-shadow:0 14px 40px rgba(0,0,0,0.5);"/>
    </div>
    """

    # Simple compact hero: show page title and short subtitle
    sim2d_html = """
    <div class="hero" style="padding:18px 8px;margin-bottom:12px;">
        <h2 style="color:#aee9ff;margin:0;font-family:Orbitron, sans-serif;">Exoplanet Explorer</h2>
        <div style="color:#dfefff;margin-top:6px;">Exoplanet Simulator and Classifier — {page}</div>
    </div>
    """
    # Use same compact hero for 3D preview placeholder (removed graphic)
    sim3d_html = sim2d_html

    if page_selected == "2D Simulator":
        st.markdown(sim2d_html.format(page="2D Simulator"), unsafe_allow_html=True)
    elif page_selected == "3D Simulator":
        st.markdown(sim3d_html.format(page="3D Simulator"), unsafe_allow_html=True)
    else:
        st.markdown(intro_html, unsafe_allow_html=True)


render_hero(page)

# --- Asistente virtual para usuarios noveles (barra lateral) ---
if "assistant_messages" not in st.session_state:
    st.session_state.assistant_messages = [
        (
            "bot",
            "Hello 👋, I'm the assistant. I can help you use the 2D/3D simulator and classifier. Ask things like: 'How do I load data?' or 'How do I add an exoplanet?'",
        )
    ]


def generate_fallback_reply(user_text: str) -> str:
    t = user_text.lower()
    # Preguntas sobre exoplanetas (español)
    if (
        "exoplanet" in t
        or "exoplaneta" in t
        or "qué es un exoplaneta" in t
        or "que es un exoplaneta" in t
    ):
        return (
            "An exoplanet (or extrasolar planet) is a planet that orbits a star outside the Solar System. "
            "They are mainly detected by the transit method (when the planet passes in front of its star and produces a small decrease in brightness), "
            "by radial velocities (variations in the star's velocity due to the planet's gravity), and by direct imaging or gravitational microlensing. "
            "Exoplanets can vary greatly in size and temperature: from gas giants larger than Jupiter to rocky planets smaller than Earth. "
            "If you want, I can explain in more detail the detection methods or how to interpret the CSV columns."
        )
    if "3d" in t or "3 d" in t:
        return "To use the 3D simulator: go to '3D Simulator' from the menu and use the controls to adjust scale and colors. If you don't see points, check that the CSV 'ML/exoplanets_visual.csv' exists."
    if "2d" in t:
        return "In '2D Simulator' you can see the RA/Dec distribution. Use the form to add an exoplanet and the prediction button if you have the models in the ML/ folder."
    if "csv" in t or "data" in t:
        return "The expected data file is at 'Pagina_web_en_24/ML/exoplanets_visual.csv'. If it doesn't exist, copy the CSV there or update the path in the code."
    if "model" in t or "predict" in t:
        return "To enable ML predictions you need 'exoplanet_classifier.joblib', 'scaler.joblib' and 'label_encoder.joblib' in the ML/ folder. If they're not there, the form will still allow adding exoplanets but without prediction."
    return "I can help you with: how to use the 2D/3D simulators, how to add exoplanets, or how to prepare ML files. Ask a specific question or write 'help'."


with st.sidebar.expander("Beginner's Assistant 🤖", expanded=False):
    for role, msg in st.session_state.assistant_messages:
        if role == "bot":
            st.markdown(f"**Assistant:** {msg}")
        else:
            st.markdown(f"**You:** {msg}")

    # Campo de entrada para preguntas del usuario
    user_question = st.text_input(
        "Type your question here:",
        key="assistant_input",
        placeholder="How can I use the simulator?",
    )
    if st.button("Send question", key="send_question"):
        if user_question and user_question.strip():
            # Agregar pregunta del usuario
            st.session_state.assistant_messages.append(("user", user_question))
            # Generar respuesta del asistente
            bot_reply = generate_fallback_reply(user_question)
            st.session_state.assistant_messages.append(("bot", bot_reply))
            # Recargar para mostrar la conversación actualizada
            st.rerun()

if page == "2D Simulator":
    st.header("2D Simulator")
    st.write(
        "Here you can display your 2D simulator. You can adapt this space to show visualizations, load data, etc."
    )
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
        st.info(f"Data file not found for 2D simulator. Searched at: {data_path}")
        df = pd.DataFrame()

    # Cargar KOI para información adicional (si existe)
    koi_path = os.path.join(base_dir, "ML", "koi_completo.csv")
    koi_dict = {}
    if os.path.exists(koi_path):
        try:
            koi_df = pd.read_csv(koi_path)
            koi_ex = koi_df.to_dict(orient="records")
            koi_dict = {str(k.get("kepoi_name")): k for k in koi_ex}
        except Exception:
            koi_dict = {}

    # Normalizar y preparar columnas necesarias
    if not df.empty:
        df = df.copy()
        if "ra" in df.columns and "dec" in df.columns:
            df["x"] = (df["ra"] - df["ra"].min()) / (df["ra"].max() - df["ra"].min())
            df["y"] = (df["dec"] - df["dec"].min()) / (
                df["dec"].max() - df["dec"].min()
            )
        else:
            df["x"] = 0.0
            df["y"] = 0.0
        if "pl_rade" in df.columns:
            df["pl_rade"] = pd.to_numeric(df["pl_rade"], errors="coerce").fillna(0.5)
        else:
            df["pl_rade"] = 0.5
    else:
        # DataFrame vacío: crear columnas mínimas
        df = pd.DataFrame(
            columns=["pl_name", "hostname", "ra", "dec", "pl_rade", "pl_eqt", "x", "y"]
        )

    # Inicializar estado de sesión con el dataframe
    if "exo_df" not in st.session_state:
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

    # Move controls to the sidebar so main content can use full width
    with st.sidebar.expander("Add new exoplanet", expanded=False):
        st.subheader("Add new exoplanet")
        with st.form("add_exo_form"):
            name = st.text_input("Name")
            ra = st.number_input("RA (0-360)", value=0.0)
            dec = st.number_input("Dec (-90 to 90)", value=0.0)
            rade = st.number_input("Radius R⊕", value=1.0)
            eqt = st.number_input("Temperature K", value=0.0)
            snr = st.number_input("Transit Signal-to-Noise", value=10.0)
            sma = st.number_input("Orbit Semi-major Axis [au]", value=0.0)
            period = st.number_input("Orbital Period [days]", value=1.0)
            dur = st.number_input("Transit Duration [hrs]", value=1.0)
            steff = st.number_input("Stellar Effective Temperature [K]", value=5600.0)
            depth = st.number_input("Transit Depth [ppm]", value=0.0)
            slogg = st.number_input(
                "Stellar Surface Gravity [log10(cm/s**2)]", value=4.4
            )
            srad = st.number_input("Stellar Radius [Solar radii]", value=1.0)
            time0bk = st.number_input("Transit Epoch [BKJD]", value=2459000.0)
            submitted = st.form_submit_button("Add and predict")

        if submitted:
            if not name:
                st.sidebar.warning("Enter a name for the exoplanet")
            else:
                features = [
                    snr,
                    rade,
                    sma,
                    eqt,
                    period,
                    dur,
                    depth,
                    steff,
                    slogg,
                    srad,
                    time0bk,
                ]
                pred_label = None
                if model is not None and scaler is not None and encoder is not None:
                    try:
                        Xs = scaler.transform([features])
                        p = model.predict(Xs)
                        pred_label = encoder.inverse_transform(p)[0]
                    except Exception as e:
                        st.sidebar.error(f"Error al predecir: {e}")

                try:
                    if (
                        len(exo_df) > 0
                        and "ra" in exo_df.columns
                        and "dec" in exo_df.columns
                        and exo_df["ra"].notnull().any()
                    ):
                        x0 = (ra - exo_df["ra"].min()) / (
                            exo_df["ra"].max() - exo_df["ra"].min()
                        )
                        y0 = (dec - exo_df["dec"].min()) / (
                            exo_df["dec"].max() - exo_df["dec"].min()
                        )
                    else:
                        x0, y0 = 0.5, 0.5
                except Exception:
                    x0, y0 = 0.5, 0.5

                new_row = {
                    "pl_name": name,
                    "hostname": name,
                    "ra": ra,
                    "dec": dec,
                    "pl_rade": rade,
                    "pl_eqt": eqt,
                    "x": x0,
                    "y": y0,
                    "pred_class": pred_label,
                }
                exo_df = pd.concat([exo_df, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.exo_df = exo_df
                st.sidebar.success(
                    f"Exoplanet '{name}' added."
                    + (f" Prediction: {pred_label}" if pred_label is not None else "")
                )

    # Selection/info in sidebar
    with st.sidebar.expander("Select / Information", expanded=False):
        st.subheader("Select / Information")
        options = exo_df["hostname"].fillna(exo_df["pl_name"]).astype(str).tolist()
        selected = st.selectbox(
            "Select an exoplanet to view details",
            options=options if options else ["-"],
        )
        if selected and selected != "-":
            row = exo_df[exo_df["hostname"].astype(str) == selected].iloc[-1]
            st.markdown(f"**Name:** {row.get('pl_name', '')}")
            st.markdown(f"**Radius:** {row.get('pl_rade', '')} R⊕")
            st.markdown(f"**Temperature:** {row.get('pl_eqt', '')} K")
            st.markdown(f"**RA, Dec:** {row.get('ra', '')}, {row.get('dec', '')}")
            if pd.notna(row.get("pred_class")):
                st.markdown(f"**Prediction (ML):** {row.get('pred_class')}")
            koi_key = str(selected)
            if koi_key in koi_dict:
                k = koi_dict[koi_key]
                st.markdown(f"**KOI disposition:** {k.get('koi_disposition')}")
                st.markdown(f"**KOI prad:** {k.get('koi_prad')}")

    # Main visualization area (full width)
    st.markdown(
        "<div style='font-size:16px;color:#aee9ff;margin-bottom:6px;'>2D Graph</div>",
        unsafe_allow_html=True,
    )
    size_scale = st.sidebar.slider("Point size scale (2D)", 1.0, 50.0, 10.0)

    plot_df = exo_df.copy()
    plot_df["size_plot"] = plot_df["pl_rade"].astype(float).fillna(0.5) * size_scale
    # Marcar seleccionado para agrandar
    if selected and selected != "-":
        plot_df["selected"] = plot_df["hostname"].astype(str) == selected
        # Aumentar tamaño del seleccionado
        plot_df.loc[plot_df["selected"], "size_plot"] = (
            plot_df.loc[plot_df["selected"], "size_plot"] * 2.5
        )
    else:
        plot_df["selected"] = False

    try:
        fig = px.scatter(
            plot_df,
            x="x",
            y="y",
            size="size_plot",
            color="pl_eqt" if "pl_eqt" in plot_df.columns else None,
            hover_name="pl_name",
            hover_data=["hostname", "pl_rade", "pl_eqt"],
            title="2D Distribution of exoplanets (normalized RA/Dec)",
            labels={"x": "RA (normalized)", "y": "Dec (normalized)"},
        )
        fig.update_layout(height=700)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating chart: {e}")

    st.subheader("Exoplanet Table")
    st.dataframe(exo_df.reset_index(drop=True))

elif page == "3D Simulator":
    st.header("3D Simulator — NASA Project")
    st.write(
        "Here you can display your 3D simulator. You can adapt this space to show visualizations, load data, etc."
    )

    # Constantes de conversión
    PC_TO_LY = 3.26156
    PC_TO_AU = 206264.8
    DAY_TO_YEAR = 1 / 365.25
    CAMERA_INITIAL_DISTANCE = 1.0
    CAMERA_SEARCH_ZOOM_FACTOR = 0.05
    RANGO_MAX_FIJO_PC = 3000.0

    # Cargar datos: preferir st.session_state.exo_df si existe, si no intentar leer el CSV del proyecto
    df3 = st.session_state.get("exo_df", pd.DataFrame()).copy()
    if df3.empty:
        project_csv = os.path.join(base_dir, "proyecto nasa", "exoplanets_visual.csv")
        fallback_csv = os.path.join(base_dir, "ML", "exoplanets_visual.csv")
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
        st.info(
            "No data to display in 3D. Place 'exoplanets_visual.csv' in 'proyecto nasa/' or 'ML/' or add exoplanets from the 2D simulator."
        )
    else:
        # Cargar modelos ML si están disponibles (misma lógica que en otras pestañas)
        model3, scaler3, encoder3 = None, None, None
        try:
            model3 = joblib.load(
                os.path.join(base_dir, "ML", "exoplanet_classifier.joblib")
            )
            scaler3 = joblib.load(os.path.join(base_dir, "ML", "scaler.joblib"))
            encoder3 = joblib.load(os.path.join(base_dir, "ML", "label_encoder.joblib"))
        except Exception:
            model3 = scaler3 = encoder3 = None

        # Move 3D controls and ML forms to the sidebar so the 3D canvas can fill the page
        with st.sidebar.expander("Controls & ML Classifier", expanded=False):
            st.subheader("Controls & ML Classifier")

            required_features = [
                "koi_model_snr",
                "koi_prad",
                "koi_sma",
                "koi_teq",
                "koi_period",
                "koi_duration",
                "koi_depth",
                "koi_steff",
                "koi_slogg",
                "koi_srad",
                "koi_time0bk",
            ]
            can_batch_predict = (
                model3 is not None
                and scaler3 is not None
                and encoder3 is not None
                and all(feat in df3.columns for feat in required_features)
            )
            if can_batch_predict:
                if st.button("Predict ML classification for entire dataset"):
                    try:
                        X_batch = df3[required_features].fillna(0).astype(float).values
                        Xs_batch = scaler3.transform(X_batch)
                        preds = model3.predict(Xs_batch)
                        df3["pred_class"] = encoder3.inverse_transform(preds)
                        st.session_state["exo_df"] = df3
                        st.success(
                            "Batch prediction completed: 'pred_class' column added to dataset."
                        )
                        try:
                            st.experimental_rerun()
                        except Exception:
                            pass
                    except Exception as e:
                        st.error(f"Error en predicción por lote: {e}")
            else:
                if model3 is None:
                    st.info(
                        "ML model not found in ML/. Place exoplanet_classifier.joblib, scaler.joblib and label_encoder.joblib in the ML/ folder."
                    )

            st.markdown("---")
            st.subheader("Predict and add (individual)")
            with st.form("ml_3d_form_left"):
                st.markdown("Enter the 11 features to predict the exoplanet class:")
                c1, c2, c3 = st.columns(3)
                with c1:
                    koi_model_snr_3 = st.number_input(
                        "Transit SNR", value=18.0, key="snr_3_left"
                    )
                    koi_prad_3 = st.number_input(
                        "Planetary Radius (koi_prad)", value=0.59, key="prad_3_left"
                    )
                    koi_sma_3 = st.number_input(
                        "Orbit SMA (koi_sma)", value=0.0739, key="sma_3_left"
                    )
                    koi_teq_3 = st.number_input(
                        "Equilibrium Temp (koi_teq)", value=443.0, key="teq_3_left"
                    )
                with c2:
                    koi_period_3 = st.number_input(
                        "Orbital Period (koi_period)",
                        value=10.3128,
                        key="period_3_left",
                    )
                    koi_duration_3 = st.number_input(
                        "Transit Duration (koi_duration)",
                        value=3.2,
                        key="duration_3_left",
                    )
                    koi_depth_3 = st.number_input(
                        "Transit Depth (koi_depth)", value=0.45, key="depth_3_left"
                    )
                    koi_steff_3 = st.number_input(
                        "Stellar Teff (koi_steff)", value=5600.0, key="steff_3_left"
                    )
                with c3:
                    koi_slogg_3 = st.number_input(
                        "Stellar logg (koi_slogg)", value=4.4, key="slogg_3_left"
                    )
                    koi_srad_3 = st.number_input(
                        "Stellar Radius (koi_srad)", value=0.98, key="srad_3_left"
                    )
                    koi_time0bk_3 = st.number_input(
                        "Transit Epoch (koi_time0bk)",
                        value=2459000.123,
                        key="time0bk_3_left",
                    )
                add_to_plot = st.checkbox(
                    "Add point to 3D plot with prediction", value=False
                )
                ml_submitted = st.form_submit_button("Predict class (ML)")

            if ml_submitted:
                if model3 is None or scaler3 is None or encoder3 is None:
                    st.error(
                        "ML model not found in ML/. Place exoplanet_classifier.joblib, scaler.joblib and label_encoder.joblib in the ML/ folder."
                    )
                else:
                    features3 = [
                        [
                            koi_model_snr_3,
                            koi_prad_3,
                            koi_sma_3,
                            koi_teq_3,
                            koi_period_3,
                            koi_duration_3,
                            koi_depth_3,
                            koi_steff_3,
                            koi_slogg_3,
                            koi_srad_3,
                            koi_time0bk_3,
                        ]
                    ]
                    try:
                        Xs3 = scaler3.transform(features3)
                        p3 = model3.predict(Xs3)
                        pred_label3 = encoder3.inverse_transform(p3)[0]
                        st.success(f"Prediction: {pred_label3}")
                        if add_to_plot:
                            new_name = f"ML_added_{len(st.session_state.exo_df) + 1}"
                            new_row = {
                                "pl_name": new_name,
                                "hostname": new_name,
                                "ra": 0.0,
                                "dec": 0.0,
                                "pl_rade": koi_prad_3,
                                "pl_eqt": koi_teq_3,
                                "x": 0.5,
                                "y": 0.5,
                                "pred_class": pred_label3,
                            }
                            st.session_state.exo_df = pd.concat(
                                [st.session_state.exo_df, pd.DataFrame([new_row])],
                                ignore_index=True,
                            )
                            st.info(f"Point added: {new_name}")
                    except Exception as e:
                        st.error(f"Error in ML prediction: {e}")

            st.markdown("---")
            st.subheader("Select / Information")
            options3 = df3["hostname"].fillna(df3["pl_name"]).astype(str).tolist()
            selected3 = st.selectbox(
                "Select an exoplanet to view details",
                options=options3 if options3 else ["-"],
            )

        # Main 3D area: compact header and sidebar slider for marker size
        st.markdown(
            "<div style='font-size:16px;color:#aee9ff;margin-bottom:6px;'>3D Visualization</div>",
            unsafe_allow_html=True,
        )
        size_scale_3d = st.sidebar.slider("Point size scale (3D)", 1.0, 50.0, 8.0)
        # preparar tamaños de marker
        df3["size_plot"] = df3["pl_rade"].astype(float).fillna(0.5) * size_scale_3d

        # Marcar seleccionado para agrandar
        if "selected3" in locals() and selected3 and selected3 != "-":
            df3["selected"] = df3["hostname"].astype(str) == selected3
            df3.loc[df3["selected"], "size_plot"] = (
                df3.loc[df3["selected"], "size_plot"] * 2.5
            )
        else:
            df3["selected"] = False

        # el plotting se realiza más abajo usando df3 y fig_data_highlight
        # Asegurar columnas y tipos
        for col in [
            "ra",
            "dec",
            "sy_dist",
            "st_teff",
            "pl_name",
            "pl_orbper",
            "pl_eqt",
        ]:
            if col not in df3.columns:
                df3[col] = np.nan
        for col in ["ra", "dec", "sy_dist", "st_teff", "pl_orbper", "pl_eqt"]:
            df3[col] = pd.to_numeric(df3[col], errors="coerce")

        # Filtrado suave similar al proyecto
        df3 = df3.dropna(subset=["ra", "dec", "sy_dist", "pl_name"])
        df3 = df3[df3["sy_dist"] > 0.01]
        df3 = df3[(df3["ra"] >= 0) & (df3["ra"] <= 360)]
        df3 = df3[(df3["dec"] >= -90) & (df3["dec"] <= 90)]
        df3 = df3[(df3["st_teff"] >= 1000) & (df3["st_teff"] <= 10000)]

        # Units and controls
        st.sidebar.subheader("Controls - NASA Project")
        unit = st.sidebar.selectbox("Units", options=["pc", "ly", "au"], index=0)
        planet_options = sorted(df3["pl_name"].dropna().unique().tolist())
        planet_sel = st.sidebar.selectbox(
            "Search exoplanet by name", options=["(none)"] + planet_options
        )
        unit_name = "pc"
        if unit == "pc":
            dist_col = "sy_dist"
            unit_name = "pc"
            factor_conversion = 1.0
        elif unit == "ly":
            dist_col = "sy_dist_ly" if "sy_dist_ly" in df3.columns else "sy_dist"
            unit_name = "al"
            factor_conversion = PC_TO_LY
            if "sy_dist_ly" not in df3.columns:
                df3["sy_dist_ly"] = df3["sy_dist"] * PC_TO_LY
        else:
            dist_col = "sy_dist_au" if "sy_dist_au" in df3.columns else "sy_dist"
            unit_name = "UA"
            factor_conversion = PC_TO_AU
            if "sy_dist_au" not in df3.columns:
                df3["sy_dist_au"] = df3["sy_dist"] * PC_TO_AU

        # Convertir a radianes
        df3["ra_rad"] = np.deg2rad(df3["ra"])
        df3["dec_rad"] = np.deg2rad(df3["dec"])

        # Calcular coordenadas 3D
        df3["x"] = df3[dist_col] * np.cos(df3["dec_rad"]) * np.cos(df3["ra_rad"])
        df3["y"] = df3[dist_col] * np.cos(df3["dec_rad"]) * np.sin(df3["ra_rad"])
        df3["z"] = df3[dist_col] * np.sin(df3["dec_rad"])

        # Rango dinámico
        RANGO_MAX_DINAMICO = RANGO_MAX_FIJO_PC * factor_conversion
        RANGO_FIJO_DINAMICO = [-RANGO_MAX_DINAMICO, RANGO_MAX_DINAMICO]

        # Colores por temp
        temp_min_planet = df3["pl_eqt"].min()
        temp_max_planet = df3["pl_eqt"].max()
        if (
            temp_min_planet == temp_max_planet
            or pd.isna(temp_min_planet)
            or pd.isna(temp_max_planet)
        ):
            temp_min_planet = 100
            temp_max_planet = 3000

        # Cámara por defecto
        INITIAL_DIST_ADJUSTED = CAMERA_INITIAL_DISTANCE * factor_conversion
        default_camera = dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(
                x=INITIAL_DIST_ADJUSTED,
                y=INITIAL_DIST_ADJUSTED,
                z=INITIAL_DIST_ADJUSTED,
            ),
        )

        final_camera = default_camera
        search_message = ""
        fig_data_highlight = []

        # If a planet was selected, center and highlight
        if planet_sel and planet_sel != "(none)":
            sel_row = df3[df3["pl_name"] == planet_sel]
            if not sel_row.empty:
                x_t = sel_row["x"].iloc[0]
                y_t = sel_row["y"].iloc[0]
                z_t = sel_row["z"].iloc[0]
                distancia_muestra = sel_row[dist_col].iloc[0]

                MAX_FOR_ZOOM = RANGO_MAX_DINAMICO
                zoom_dist_search = MAX_FOR_ZOOM * CAMERA_SEARCH_ZOOM_FACTOR
                zoom_camera = dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=x_t, y=y_t, z=z_t),
                    eye=dict(
                        x=x_t + zoom_dist_search,
                        y=y_t + zoom_dist_search,
                        z=z_t + zoom_dist_search,
                    ),
                )
                final_camera = zoom_camera

                # estado confirmado/candidato heurístico
                if planet_sel.split(" ")[-1].isalpha() and not planet_sel.endswith(
                    ".01"
                ):
                    estado = "CONFIRMED ✅"
                else:
                    estado = "CANDIDATE ⚠️"

                temp_eqt_val = sel_row["pl_eqt"].iloc[0]
                temp_display = (
                    f"{temp_eqt_val:.0f} K" if not pd.isna(temp_eqt_val) else "N/D"
                )

                search_message = f"Status: {estado} | Planet: {planet_sel} | Distance: {distancia_muestra:.2f} {unit_name} | Planet T°: {temp_display}."

                fig_data_highlight = [
                    go.Scatter3d(
                        x=[x_t],
                        y=[y_t],
                        z=[z_t],
                        mode="markers",
                        marker=dict(
                            size=12,
                            color="#00BFFF",
                            symbol="circle",
                            line=dict(width=2, color="white"),
                        ),
                        name=planet_sel,
                        hoverinfo="text",
                        text=[
                            f"🌟 ¡OBJETO BUSCADO!<br>{planet_sel}<br>Dist: {distancia_muestra:.2f} {unit_name}<br>T: {temp_display}"
                        ],
                        showlegend=False,
                    )
                ]

        # Construir figura
        # Preparar textos de hover fuera de la lista de datos para evitar sintaxis inválida
        per_series = df3.get("pl_orbper", pd.Series([np.nan] * len(df3)))
        hover_texts = []
        for n, d, t, p in zip(df3["pl_name"], df3[dist_col], df3["pl_eqt"], per_series):
            if pd.isna(t):
                hover_texts.append(
                    f"Name: {n}<br>Planet T°: N/A<br>Distance: {d:.2f} {unit_name}"
                )
            else:
                # convertir periodo a años si es posible
                try:
                    per_yr = float(p) * DAY_TO_YEAR if (not pd.isna(p)) else None
                except Exception:
                    per_yr = None
                if per_yr is not None and not pd.isna(per_yr):
                    hover_texts.append(
                        f"Name: {n}<br>Planet T°: {t:.0f} K<br>Distance: {d:.2f} {unit_name}<br>Period: {per_yr:.2f} years"
                    )
                else:
                    hover_texts.append(
                        f"Name: {n}<br>Planet T°: {t:.0f} K<br>Distance: {d:.2f} {unit_name}"
                    )

        # Prepare data and color by temperature
        color_col = "pl_eqt"
        marker_dict = dict(
            size=4,
            color=df3["pl_eqt"],
            colorscale="Plasma",
            cmin=temp_min_planet,
            cmax=temp_max_planet,
            colorbar=dict(title="Planet Temp. (K)", thickness=20),
            opacity=0.8,
            line=dict(width=0.2, color="white"),
        )

        # Crear scatter3d para los exoplanetas; si es categórico, crear una traza por categoría para la leyenda
        # Ajustar tamaños relativos según el radio (mejor visibilidad)
        sizes = (
            df3["pl_rade"].astype(float).fillna(0.5)
            - df3["pl_rade"].astype(float).fillna(0.5).min()
        )
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
            star_x = rng.uniform(
                RANGO_FIJO_DINAMICO[0] * 0.9, RANGO_FIJO_DINAMICO[1] * 0.9, n_stars
            )
            star_y = rng.uniform(
                RANGO_FIJO_DINAMICO[0] * 0.9, RANGO_FIJO_DINAMICO[1] * 0.9, n_stars
            )
            star_z = rng.uniform(
                RANGO_FIJO_DINAMICO[0] * 0.9, RANGO_FIJO_DINAMICO[1] * 0.9, n_stars
            )
            star_trace = go.Scatter3d(
                x=star_x,
                y=star_y,
                z=star_z,
                mode="markers",
                marker=dict(size=1.5, color="white", opacity=0.15),
                hoverinfo="none",
                showlegend=False,
            )
            traces.append(star_trace)
        except Exception:
            pass

        # Continuous temperature coloring
        traces.append(
            go.Scatter3d(
                x=df3["x"],
                y=df3["y"],
                z=df3["z"],
                mode="markers",
                marker=dict(
                    size=sizes,
                    color=df3["pl_eqt"],
                    colorscale="Plasma",
                    cmin=temp_min_planet,
                    cmax=temp_max_planet,
                    colorbar=dict(title="Planet Temp. (K)", thickness=20),
                    opacity=0.85,
                    line=dict(width=0.2, color="white"),
                ),
                name="Exoplanets",
                text=hover_texts,
                hovertemplate=hovertemplate,
                hoverinfo="text",
            )
        )

        # Solar System central point
        traces.insert(
            len(traces),
            go.Scatter3d(
                x=[0],
                y=[0],
                z=[0],
                mode="markers",
                marker=dict(
                    size=10,
                    color="gold",
                    symbol="diamond",
                    line=dict(width=1, color="white"),
                ),
                name="Solar System",
                hoverinfo="text",
                text=["Solar System (Earth)"],
            ),
        )

        # Añadir highlight si aplica
        traces = traces + fig_data_highlight

        fig = go.Figure(data=traces)
        fig.update_layout(
            title=f"Exoplanets in 3D (in {unit_name})",
            scene=dict(
                xaxis=dict(
                    range=RANGO_FIJO_DINAMICO,
                    backgroundcolor="#000010",
                    gridcolor="#222222",
                    zerolinecolor="#333333",
                    title=f"X ({unit_name})",
                ),
                yaxis=dict(
                    range=RANGO_FIJO_DINAMICO,
                    backgroundcolor="#000010",
                    gridcolor="#222222",
                    zerolinecolor="#333333",
                    title=f"Y ({unit_name})",
                ),
                zaxis=dict(
                    range=RANGO_FIJO_DINAMICO,
                    backgroundcolor="#000010",
                    gridcolor="#222222",
                    zerolinecolor="#333333",
                    title=f"Z ({unit_name})",
                ),
                aspectmode="cube",
                camera=final_camera,
                uirevision=planet_sel if planet_sel else "PersistentView",
            ),
            height=820,
            paper_bgcolor="#070712",
            plot_bgcolor="#070712",
            font=dict(color="white"),
            margin=dict(l=0, r=0, t=50, b=0),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        # Mejoras al hoverlabel
        fig.update_traces(hoverlabel=dict(bgcolor="#111111", font_color="white"))

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
                koi_model_snr = st.number_input(
                    "Transit Signal-to-Noise (koi_model_snr)", value=18.0
                )
                koi_prad = st.number_input("Planetary Radius (koi_prad)", value=0.59)
                koi_sma = st.number_input(
                    "Orbit Semi-Major Axis [au] (koi_sma)", value=0.0739
                )
                koi_teq = st.number_input(
                    "Equilibrium Temperature [K] (koi_teq)", value=443.0
                )
            with col2:
                koi_period = st.number_input(
                    "Orbital Period [days] (koi_period)", value=10.3128
                )
                koi_duration = st.number_input(
                    "Transit Duration [hrs] (koi_duration)", value=3.2
                )
                koi_depth = st.number_input(
                    "Transit Depth [ppm] (koi_depth)", value=0.45
                )
                koi_steff = st.number_input(
                    "Stellar Effective Temperature [K] (koi_steff)", value=5600.0
                )
            with col3:
                koi_slogg = st.number_input(
                    "Stellar Surface Gravity [log10(cm/s**2)] (koi_slogg)", value=4.4
                )
                koi_srad = st.number_input(
                    "Stellar Radius [Solar radii] (koi_srad)", value=0.98
                )
                koi_time0bk = st.number_input(
                    "Transit Epoch [BKJD] (koi_time0bk)", value=2459000.123
                )
            submitted = st.form_submit_button("Predict class")
        if submitted:
            features = [
                [
                    koi_model_snr,
                    koi_prad,
                    koi_sma,
                    koi_teq,
                    koi_period,
                    koi_duration,
                    koi_depth,
                    koi_steff,
                    koi_slogg,
                    koi_srad,
                    koi_time0bk,
                ]
            ]
            X_scaled = scaler.transform(features)
            pred = model.predict(X_scaled)
            clase = encoder.inverse_transform(pred)
            st.success(f"Predicción: {clase[0]}")
    except Exception as e:
        st.error(f"Error cargando el modelo o scaler: {e}")
