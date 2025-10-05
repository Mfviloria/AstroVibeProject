import pandas as pd
import numpy as np
import os

# --- Cargar dataset unificado ---
try:
    df = pd.read_csv("exoplanets_dataset.csv")
except FileNotFoundError:
    print("ERROR: No se encontró 'exoplanets_dataset.csv'. Ejecuta 'unificar_datasets.py' primero.")
    exit()

# --- LIMPIEZA GENERAL Y CONVERSIÓN ---
cols_to_numeric = [
    'pl_orbper', 'pl_rade', 'pl_bmasse', 'pl_eqt', 
    'st_teff', 'st_rad', 'st_mass', 'sy_dist', 'ra', 'dec'
]
for col in cols_to_numeric:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Rellenar valores de temperatura faltantes con la mediana
if 'st_teff' in df.columns:
    df['st_teff'] = df['st_teff'].fillna(df['st_teff'].median())

# Rellenar valores de nombre faltantes
if 'pl_name' in df.columns:
    df['pl_name'] = df['pl_name'].fillna('Unknown')
    df = df.drop_duplicates(subset=['pl_name'])

# =============================
# 2) DATASET PARA VISUALIZACIÓN (VISUAL)
# =============================
cols_visual_base = [
    "pl_name", "hostname", "pl_orbper", "pl_rade", "pl_bmasse", "pl_eqt", "ra", "dec", 
    "st_teff", "st_rad", "st_mass", "sy_dist", "disc_year", "discoverymethod", "source"
] 
cols_visual = [col for col in cols_visual_base if col in df.columns]

df_visual = df[cols_visual].copy()

# *** FILTRADO CRÍTICO AQUÍ: ELIMINAR CUALQUIER FILA SIN COORDENADAS O DISTANCIA ***
# Si falta cualquiera de estas, la coordenada 3D será (0,0,0) o NaN.
df_visual = df_visual.dropna(subset=['ra', 'dec', 'sy_dist'])

# Adicionalmente, eliminar distancias negativas o cero.
df_visual = df_visual[df_visual['sy_dist'] > 0.0]

# Guardar dataset para visualización (ESTE ES EL ARCHIVO LIMPIO)
df_visual.to_csv("exoplanets_visual.csv", index=False)
print("✅ Dataset para visualización (exoplanets_visual.csv) creado. ¡Filas con NaN en coordenadas ELIMINADAS!")
print(f"Dimensiones de exoplanets_visual.csv: {df_visual.shape[0]} filas limpias.")