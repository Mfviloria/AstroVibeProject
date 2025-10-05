# unificar_datasets.py
# Script para combinar los datasets FULL y filtrar a las columnas más útiles.

import pandas as pd
import numpy as np

# --- ESTRUCTURA DE COLUMNAS ÚTILES (16 columnas) ---
COLUMNAS_FINALES_DASH_Y_ANALISIS = [
    # 1. UBICACIÓN (3)
    "ra", "dec", "sy_dist", 
    
    # 2. IDENTIDAD Y COLOR (3)
    "pl_name", "hostname", "pl_eqt",
    
    # 3. PROPIEDADES PLANETARIAS FÍSICAS (3)
    "pl_rade",   # Radio del planeta
    "pl_bmasse", # Masa del planeta
    "pl_orbper", # Período orbital
    
    # 4. PROPIEDADES ESTELARES (3)
    "st_teff",   # Temperatura de la estrella (K)
    "st_mass",   # Masa de la estrella
    "st_rad",    # Radio de la estrella
    
    # 5. CONTEXTO Y HABITABILIDAD (4)
    "discoverymethod", 
    "disc_year", 
    "pl_insol",  # Flujo de insolación (Métrica de habitabilidad)
    "pl_orbeccen" # Excentricidad orbital
]

# Rutas de los archivos FULL generados
file_paths = ["kepler_koi_FULL.csv", "tess_toi_FULL.csv", "k2_planets_FULL.csv"]
combined_data = []

print("Iniciando unificación de bases de datos con filtrado a columnas útiles...")

for file in file_paths:
    try:
        # Cargamos los DataFrames recolectados con todas las columnas
        df = pd.read_csv(file)
        combined_data.append(df)
        print(f"  - Añadido {file} con {len(df.columns)} columnas iniciales.")
    except FileNotFoundError:
        print(f"  - ❌ Archivo {file} no encontrado. Asegúrate de correr el script de descarga primero.")
    except Exception as e:
        print(f"  - ❌ Error al procesar {file}: {e}")

if combined_data:
    # 1. Concatenar todos los DataFrames
    final_df = pd.concat(combined_data, ignore_index=True)
    
    # 2. Eliminar duplicados
    final_df.drop_duplicates(subset=['pl_name'], keep='first', inplace=True)
    
    # 3. FILTRADO FINAL: Filtramos para quedarnos SOLAMENTE con las 16 columnas útiles.
    df_filtrado = pd.DataFrame(index=final_df.index)
    
    for col in COLUMNAS_FINALES_DASH_Y_ANALISIS:
        if col in final_df.columns:
            df_filtrado[col] = final_df[col]
        else:
            # Si una columna esencial no se encontró en la descarga, la rellenamos con NaN
            df_filtrado[col] = np.nan
    
    # 4. Guardar la base de datos final
    df_filtrado.to_csv("exoplanets_visual.csv", index=False)
    
    print(f"✔ Unificación y filtrado finalizado. Creado 'exoplanets_visual.csv' con {len(df_filtrado)} filas y {len(df_filtrado.columns)} columnas finales y útiles.")
else:
    print("❌ No se pudo encontrar ninguna base de datos para unificar.")