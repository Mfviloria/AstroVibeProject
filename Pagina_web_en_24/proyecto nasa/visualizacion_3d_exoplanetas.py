import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State 
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats 

# --- CONSTANTES DE CONVERSIÓN ---
PC_TO_LY = 3.26156    # 1 parsec = 3.26156 años luz
PC_TO_AU = 206264.8   # 1 parsec = 206,264.8 UA
DAY_TO_YEAR = 1 / 365.25 # 1 día a años

# --- CONFIGURACIÓN DE LA VISUALIZACIÓN ---
INTERVALO_ACTUALIZACION_MS = 10000 
CAMERA_INITIAL_DISTANCE = 1500.0 
CAMERA_SEARCH_ZOOM_FACTOR = 0.05 
DATA_FILE = "exoplanets_visual.csv"

# Rango máximo fijo base en parsecs (pc).
RANGO_MAX_FIJO_PC = 3000.0 


# Función de Carga de Datos y Conversiones (FILTROS SUAVIZADOS)
def load_and_prepare_data():
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo {DATA_FILE}. Usando DataFrame vacío.")
        return pd.DataFrame()

    # Se incluye 'pl_eqt' (Temperatura de Equilibrio del Planeta)
    required_cols = ['ra', 'dec', 'sy_dist', 'st_teff', 'pl_name', 'pl_orbper', 'pl_eqt']
    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan 

    for col in ['ra', 'dec', 'sy_dist', 'st_teff', 'pl_orbper', 'pl_eqt']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 1. FILTRADO ESTRICTO (SUAVIZADO)
    
    # LÍNEA CLAVE: Solo se eliminan si NO tienen las coordenadas y el nombre. 
    # Los planetas sin 'pl_eqt' (temperatura) se mantienen.
    df = df.dropna(subset=['ra', 'dec', 'sy_dist', 'pl_name'])
    
    # Se mantienen los filtros de rangos físicos básicos
    df = df[df['sy_dist'] > 0.01] 
    df = df[(df['ra'] >= 0) & (df['ra'] <= 360)] 
    df = df[(df['dec'] >= -90) & (df['dec'] <= 90)] 
    
    # Filtro de T° de la ESTRELLA (se mantiene, es útil)
    df = df[(df['st_teff'] >= 1000) & (df['st_teff'] <= 10000)]
    
    # Filtro de T° del planeta (COMENTADO para incluir más planetas)
    # df = df[(df['pl_eqt'] >= 100) & (df['pl_eqt'] <= 3000)] 
    
    # Filtro Z-Score de Distancia (COMENTADO para incluir objetos muy lejanos)
    # if len(df) > 10:
    #     df_temp = df.copy()
    #     df_temp = df_temp[np.abs(stats.zscore(df_temp['sy_dist'])) < 3]
    #     if len(df_temp) > 10:
    #         df = df_temp 

    if df.empty:
        return pd.DataFrame()

    # 2. CONVERSIONES
    df['sy_dist_ly'] = df['sy_dist'] * PC_TO_LY
    df['sy_dist_au'] = df['sy_dist'] * PC_TO_AU
    df['pl_orbper_yr'] = df['pl_orbper'] * DAY_TO_YEAR

    # 3. CÁLCULO DE ÁNGULOS
    df['ra_rad'] = np.deg2rad(df['ra'])
    df['dec_rad'] = np.deg2rad(df['dec'])

    df = df.reset_index(drop=True)
    return df

# Inicializar Dash
app = dash.Dash(__name__)

# --- DISEÑO DE LA APLICACIÓN (CONTROLES CENTRADOS) ---
app.layout = html.Div(style={'backgroundColor': '#111111', 'color': 'white', 'padding': '20px'}, children=[
    
    html.H1("Exoplanetas en 3D (Color por T° del Planeta)", style={'textAlign': 'center', 'color': '#00BFFF', 'fontFamily': 'sans-serif'}),
    
    dcc.Interval(
        id='interval-component',
        interval=INTERVALO_ACTUALIZACION_MS,
        n_intervals=0
    ),
    
    # DIV CONTENEDOR DE SELECTORES (CENTRADOS)
    html.Div([
        # Selector de Planeta
        dcc.Dropdown(
            id='planet-dropdown',
            placeholder="Buscar exoplaneta por nombre...",
            style={'backgroundColor': '#222222', 'color': '#961A1A', 'width': '250px', 'display': 'inline-block', 'marginRight': '10px'}
        ),
        # Selector de Unidades
        dcc.Dropdown(
            id='unit-dropdown',
            options=[
                {'label': 'Parsecs (pc)', 'value': 'pc'},
                {'label': 'Años Luz (al)', 'value': 'ly'},
                {'label': 'Unidades Astronómicas (UA)', 'value': 'au'}
            ],
            value='pc', 
            clearable=False,
            style={'backgroundColor': '#222222', 'color': '#961A1A', 'width': '180px', 'display': 'inline-block', 'marginLeft': '10px'}
        ),
        # Mensaje de búsqueda
        html.Div(id='search-output', style={'textAlign': 'center', 'marginTop': '10px', 'color': 'white'})
    ], style={'textAlign': 'center', 'padding': '0 20px', 'marginBottom': '20px', 'width': '100%'}),

    # Store oculto para guardar la uirevision
    dcc.Store(id='uirevision-store', data=None),
    
    dcc.Graph(
        id='exoplanet-graph',
        style={'width': '100vw', 'height': '90vh'},
        config={'responsive': True, 'displaylogo': False} 
    ),
])

# --- CALLBACK 1: ACTUALIZAR DATOS Y OPCIONES DE BÚSQUEDA ---
@app.callback(
    [Output('planet-dropdown', 'options'),
     Output('planet-dropdown', 'value')],
    [Input('interval-component', 'n_intervals'),
     Input('planet-dropdown', 'value')] 
)
def update_dropdown_options(n, current_value):
    df = load_and_prepare_data()
    if df.empty:
        return [], None
    options = [{'label': name, 'value': name} for name in df['pl_name'].unique()]
    if current_value is not None and current_value not in df['pl_name'].unique():
        current_value = None
    return options, current_value

# --- CALLBACK 2: GENERAR GRÁFICA Y PERSISTENCIA DE CÁMARA (CORREGIDO) ---
@app.callback(
    [Output('exoplanet-graph', 'figure'),
     Output('search-output', 'children'),
     Output('uirevision-store', 'data')],
    [Input('planet-dropdown', 'value'),
     Input('interval-component', 'n_intervals'),
     Input('unit-dropdown', 'value')], 
    [State('exoplanet-graph', 'relayoutData'),
     State('uirevision-store', 'data')]
)
def update_graph(selected_planet_name, n, selected_unit, relayout_data, current_uirevision):
    df = load_and_prepare_data()
    
    if df.empty:
        fig = go.Figure(layout=go.Layout(
            title="No hay datos de exoplanetas después del filtrado.",
            paper_bgcolor="#111111", plot_bgcolor="#111111", font=dict(color='white')
        ))
        return fig, "No hay datos de exoplanetas para mostrar después del filtrado.", None

    # --- DETERMINAR LAS UNIDADES Y LA COLUMNA DE DISTANCIA ---
    if selected_unit == 'pc':
        dist_col = 'sy_dist'
        unit_name = 'pc'
        factor_conversion = 1.0
    elif selected_unit == 'ly':
        dist_col = 'sy_dist_ly'
        unit_name = 'al' 
        factor_conversion = PC_TO_LY
    elif selected_unit == 'au':
        dist_col = 'sy_dist_au'
        unit_name = 'UA' 
        factor_conversion = PC_TO_AU
    else: # Fallback
        dist_col = 'sy_dist'
        unit_name = 'pc'
        factor_conversion = 1.0

    # *** CÁLCULO DE COORDENADAS 3D DINÁMICO ***
    df['x'] = df[dist_col] * np.cos(df['dec_rad']) * np.cos(df['ra_rad'])
    df['y'] = df[dist_col] * np.cos(df['dec_rad']) * np.sin(df['ra_rad'])
    df['z'] = df[dist_col] * np.sin(df['dec_rad'])
    
    # Rango de los ejes ajustado a la unidad seleccionada
    RANGO_MAX_DINAMICO = RANGO_MAX_FIJO_PC * factor_conversion
    RANGO_FIJO_DINAMICO = [-RANGO_MAX_DINAMICO, RANGO_MAX_DINAMICO]

    # --- CÁLCULO DE RANGOS DE COLOR (BASADO EN T° DEL PLANETA 'pl_eqt') ---
    # Plotly ignora los NaN en el color, por lo que el min/max es solo de los valores válidos.
    temp_min_planet = df['pl_eqt'].min() 
    temp_max_planet = df['pl_eqt'].max() 
    # Asegurar que el rango no sea cero si solo hay un valor (o si están cerca)
    if temp_min_planet == temp_max_planet or pd.isna(temp_min_planet) or pd.isna(temp_max_planet):
        temp_min_planet = 100 
        temp_max_planet = 3000

    # --- LÓGICA DE CÁMARA Y UIREVISION ---
    INITIAL_DIST_ADJUSTED = CAMERA_INITIAL_DISTANCE * factor_conversion
    
    default_camera = dict(
        up=dict(x=0, y=0, z=1), 
        center=dict(x=0, y=0, z=0),
        eye=dict(x=INITIAL_DIST_ADJUSTED, y=INITIAL_DIST_ADJUSTED, z=INITIAL_DIST_ADJUSTED)
    )

    final_camera_for_fig = default_camera
    search_message = ""
    fig_data_highlight = []
    
    # 1. Definir el nuevo valor de uirevision
    if selected_planet_name:
        new_uirevision = selected_planet_name 
    else:
        new_uirevision = 'PersistentView' 
    
    # 2. Lógica de Zoom de Búsqueda (FORZADA)
    if selected_planet_name:
        selected_row = df[df['pl_name'] == selected_planet_name]
        
        if not selected_row.empty:
            x_target = selected_row['x'].iloc[0]
            y_target = selected_row['y'].iloc[0]
            z_target = selected_row['z'].iloc[0]
            distancia_muestra = selected_row[dist_col].iloc[0] 
            
            MAX_FOR_ZOOM = RANGO_MAX_DINAMICO 
            zoom_dist_search = MAX_FOR_ZOOM * CAMERA_SEARCH_ZOOM_FACTOR 
            
            zoom_camera = dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=x_target, y=y_target, z=z_target),
                eye=dict(x=x_target + zoom_dist_search, y=y_target + zoom_dist_search, z=z_target + zoom_dist_search)
            )
            
            final_camera_for_fig = zoom_camera 
            
            # Lógica de Confirmación
            if selected_planet_name.split(' ')[-1].isalpha() and not selected_planet_name.endswith('.01'):
                estado = f"**CONFIRMADO** ✅"
            else:
                estado = f"**CANDIDATO** ⚠️"
            
            # Valor de temperatura, manejando el NaN
            temp_eqt_val = selected_row['pl_eqt'].iloc[0]
            temp_display = f"{temp_eqt_val:.0f} K" if not pd.isna(temp_eqt_val) else "N/D"

            search_message = (
                f"Estado: {estado} | "
                f"Planeta: {selected_planet_name} | "
                f"Distancia: {distancia_muestra:.2f} {unit_name} | "
                f"T° Planeta: {temp_display}."
            )
            
            # Resaltar el planeta
            fig_data_highlight = [
                 go.Scatter3d(
                    x=[x_target], y=[y_target], z=[z_target], mode='markers',
                    marker=dict(size=12, color='#00BFFF', symbol='circle', line=dict(width=2, color='white')), 
                    name=selected_planet_name, hoverinfo='text',
                    text=[f"🌟 ¡OBJETO BUSCADO!<br>Estado: {estado.replace('**', '').replace(' ', '')}<br>{selected_planet_name}<br>Distancia: {distancia_muestra:.2f} {unit_name}<br>T° Planeta: {temp_display}"],
                    showlegend=False
                )
            ]
        else:
            search_message = f"⚠️ Planeta '{selected_planet_name}' no encontrado en el dataset actual."
    
    # 4. CREAR LA FIGURA
    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=[0], y=[0], z=[0], mode='markers', marker=dict(size=8, color='yellow', symbol='diamond'), name='Sistema Solar',
                hoverinfo='text', text=[f"Sistema Solar (Tierra)<br>T° Equilibrio: 255 K"]
            ),
            go.Scatter3d(
                x=df['x'], y=df['y'], z=df['z'], mode='markers',
                # COLOR BASADO EN 'pl_eqt'
                marker=dict(
                    size=4, color=df['pl_eqt'], colorscale='Plasma', cmin=temp_min_planet, cmax=temp_max_planet,
                    colorbar=dict(title='Temp. Planeta (K)', thickness=20, orientation='v', x=0.01, y=0.5), 
                    opacity=0.7, line=dict(width=0.5, color='white')
                ),
                name='Exoplanetas',
                text=[f"Nombre: {n}<br>T° Planeta: {t:.0f} K<br>Distancia: {d:.2f} {unit_name}<br>Período: {p:.2f} años" 
                      if not pd.isna(t) else f"Nombre: {n}<br>T° Planeta: N/D<br>Distancia: {d:.2f} {unit_name}<br>Período: {p:.2f} años"
                      for n, d, t, p in zip(df['pl_name'], df[dist_col], df['pl_eqt'], df['pl_orbper_yr'])],
                hoverinfo='text'
            )
        ] + fig_data_highlight,
        
        layout=go.Layout(
            title=f"Exoplanetas en 3D (Color por T° del Planeta, en {unit_name})", 
            scene=dict(
                # Rango y títulos de los ejes DINÁMICOS
                xaxis=dict(range=RANGO_FIJO_DINAMICO, backgroundcolor="#000000", gridcolor="#333333", zerolinecolor="#666666", title=f'X ({unit_name})'),
                yaxis=dict(range=RANGO_FIJO_DINAMICO, backgroundcolor="#000000", gridcolor="#333333", zerolinecolor="#666666", title=f'Y ({unit_name})'),
                zaxis=dict(range=RANGO_FIJO_DINAMICO, backgroundcolor="#000000", gridcolor="#333333", zerolinecolor="#666666", title=f'Z ({unit_name})'),
                aspectmode='cube',
                camera=final_camera_for_fig,
                # APLICACIÓN DE UIREVISION: ¡LA CLAVE DE LA SOLUCIÓN!
                uirevision=new_uirevision 
            ),
            height=800, paper_bgcolor="#111111", plot_bgcolor="#111111", font=dict(color='white')
        )
    )

    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    return fig, html.B(search_message, style={'color': '#00BFFF'}), new_uirevision

# --- EJECUTAR APLICACIÓN (BLOQUE FALTANTE, AÑADIDO AQUÍ) ---
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)