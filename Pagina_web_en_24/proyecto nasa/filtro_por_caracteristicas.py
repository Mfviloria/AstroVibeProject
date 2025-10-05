import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
import sys

# --- CONFIGURACIÓN DE VISUALIZACIÓN ---
MODO_OSCURO = True
FACTOR_ESCALA = 0.5 
ARCHIVO_SALIDA = "exoplanetas_filtrados.html"

# --- LEER Y FILTRAR DATASET ---
file = "exoplanets_dataset.csv"
try:
    df = pd.read_csv(file, low_memory=False) 
except:
    df = pd.read_csv(file)

# Limpieza básica para el filtro
if "disposition" in df.columns:
    df = df[~df["disposition"].str.contains("FALSE POSITIVE|NO PLANET", na=False, case=False)]
if "koi_disposition" in df.columns:
    df = df[~df["koi_disposition"].str.contains("FALSE POSITIVE|NO PLANET", na=False, case=False)]

# --- HERRAMIENTAS DE PROCESAMIENTO ---

def coords_cartesianas(df):
    """Calcula coordenadas cartesianas (X, Y, Z) a partir de RA, Dec y Dist."""
    ra = pd.to_numeric(df["ra"], errors="coerce")
    dec = pd.to_numeric(df["dec"], errors="coerce")
    dist = pd.to_numeric(df["sy_dist"], errors="coerce")
    mask = (~ra.isna()) & (~dec.isna()) & (~dist.isna())
    ra_rad = np.deg2rad(ra[mask])
    dec_rad = np.deg2rad(dec[mask])
    x = dist[mask] * np.cos(dec_rad) * np.cos(ra_rad)
    y = dist[mask] * np.cos(dec_rad) * np.sin(ra_rad)
    z = dist[mask] * np.sin(dec_rad)
    return x, y, z, mask

def tooltip(row):
    """Genera el texto de la etiqueta flotante (tooltip)."""
    # Simplificado, ya que las descripciones largas se asumen en el otro script.
    html = f"<b>🪐 {row.get('pl_name','Planeta Desconocido')}</b><br>"
    html += f"Método: {row.get('discoverymethod', 'N/A')}<br>" 
    html += f"Radio: {row.get('pl_rade','')} R⊕<br>"
    html += f"Temp. equilibrio: {row.get('pl_eqt','')} K<br>"
    html += f"Distancia: {row.get('sy_dist','')} pc"
    return html


def get_layout(titulo):
    """Configuración de layout para modo oscuro y ejes."""
    layout = dict(
        scene=dict(
            xaxis_title='X (pc)',
            yaxis_title='Y (pc)',
            zaxis_title='Z (pc)',
            aspectmode='cube',
        ),
        title=titulo
    )
    if MODO_OSCURO:
        layout.update(dict(
            paper_bgcolor="#111111",
            font=dict(color="#CCCCCC"),
        ))
        layout['scene'].update(dict(
            bgcolor="#111111",
            xaxis=dict(color="#CCCCCC"),
            yaxis=dict(color="#CCCCCC"),
            zaxis=dict(color="#CCCCCC"),
        ))
    return layout


def crear_figura_filtrada(df_filtrado, titulo_filtro):
    """Crea la figura 3D para el subconjunto de datos."""
    ra = pd.to_numeric(df_filtrado["ra"], errors="coerce")
    dec = pd.to_numeric(df_filtrado["dec"], errors="coerce")
    dist = pd.to_numeric(df_filtrado["sy_dist"], errors="coerce")
    eqt = pd.to_numeric(df_filtrado["pl_eqt"], errors="coerce")
    rade = pd.to_numeric(df_filtrado["pl_rade"], errors="coerce") 
    
    mask = (~ra.isna()) & (~dec.isna()) & (~dist.isna()) & (~eqt.isna()) & (~rade.isna())
    dff_valid = df_filtrado[mask]
    
    x, y, z, _ = coords_cartesianas(dff_valid)
    color = dff_valid["pl_eqt"].astype(float)
    size = dff_valid["pl_rade"].astype(float) * FACTOR_ESCALA * 2 # Radio un poco más grande
    info = [tooltip(row) for _, row in dff_valid.iterrows()]
    
    trace_planetas = go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(
            size=size, 
            color=color,
            colorscale='Viridis',  
            colorbar=dict(title="Temp. (K)"),
            opacity=0.9,
            line=dict(width=0.5, color="#222"),
            symbol='circle'
        ),
        text=info,
        hovertemplate='%{text}<extra></extra>',
        name="Exoplanetas Filtrados"
    )
    
    trace_sol = go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=10, color='red', symbol='diamond'),
        name="Sistema Solar"
    )
    
    fig = go.Figure(data=[trace_planetas, trace_sol])
    fig.update_layout(**get_layout(titulo_filtro))
    return fig

# --- EJECUCIÓN PRINCIPAL (INTERFAZ DE LÍNEA DE COMANDOS) ---
if __name__ == "__main__":
    print("\n--- HERRAMIENTA DE FILTRADO DE EXOPLANETAS POR CARACTERÍSTICAS ---")
    
    # Pedir filtros al usuario
    metodo = input("Método de descubrimiento (ej: Transit, ENTER para omitir): ") or None
    radio_min = input("Radio Mínimo (R⊕, ej: 1.0, ENTER para omitir): ") or None
    radio_max = input("Radio Máximo (R⊕, ej: 2.5, ENTER para omitir): ") or None
    
    try:
        radio_min = float(radio_min) if radio_min else None
        radio_max = float(radio_max) if radio_max else None
    except ValueError:
        print("❌ El radio debe ser un valor numérico. Cancelando.")
        sys.exit()

    dff = df.copy()
    filtros_aplicados = []

    # Aplicar filtros
    if metodo:
        dff = dff[dff["discoverymethod"].str.contains(metodo, na=False, case=False)]
        filtros_aplicados.append(f"Método: {metodo}")
    if radio_min is not None:
        dff = dff[dff["pl_rade"] >= radio_min]
        filtros_aplicados.append(f"Radio >= {radio_min} R⊕")
    if radio_max is not None:
        dff = dff[dff["pl_rade"] <= radio_max]
        filtros_aplicados.append(f"Radio <= {radio_max} R⊕")

    if dff.empty:
        print("\n❌ ¡Lo siento! No se encontraron exoplanetas que coincidan con esos criterios.")
    else:
        print(f"\n✔ Encontrados {len(dff)} exoplanetas.")
        titulo = f"Filtro: " + ", ".join(filtros_aplicados) if filtros_aplicados else "Todos los Exoplanetas"
        
        fig = crear_figura_filtrada(dff, titulo)
        
        # Guardar la figura filtrada en un nuevo HTML
        pio.write_html(fig, ARCHIVO_SALIDA, auto_open=True)
        print(f"✅ Visualización filtrada exportada a {ARCHIVO_SALIDA}. El archivo se abrirá automáticamente.")