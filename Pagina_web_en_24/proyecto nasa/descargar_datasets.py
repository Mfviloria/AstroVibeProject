# descargar_datasets.py
# Script modificado para descargar TODAS las columnas disponibles en la fuente de la NASA.

from astroquery.nasa_exoplanet_archive import NasaExoplanetArchive
import pandas as pd

# Función auxiliar para guardar CSV
def save_table(name, filename):
    print(f"Descargando {name} ...")
    try:
        # 1. DESCARGAR LA TABLA COMPLETA: Usamos select='*'
        table = NasaExoplanetArchive.query_criteria(table=name, select="*")
        df = table.to_pandas()

        # 2. GUARDAR EL ARCHIVO CON TODAS LAS COLUMNAS DISPONIBLES
        df.to_csv(filename, index=False)
        
        print(f"✔ Guardado en {filename} con {len(df)} filas y {len(df.columns)} columnas.")
        print(f"  --> Se han guardado {len(df.columns)} columnas.")
        
    except Exception as e:
        print(f"❌ Error descargando {name}: {e}")


# --- EJECUCIÓN DE DESCARGAS ---
save_table("cumulative", "kepler_koi_FULL.csv")   # Kepler/KOI
save_table("toi", "tess_toi_FULL.csv")           # TESS
save_table("k2pandc", "k2_planets_FULL.csv")      # K2

print("🚀 Descarga finalizada. Los 3 archivos contienen TODAS las columnas posibles.")
