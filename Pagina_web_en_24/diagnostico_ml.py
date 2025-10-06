#!/usr/bin/env python3
"""
Script de Diagnóstico ML - Exoplanet Explorer
==============================================
Este script verifica la compatibilidad de tus datos con el clasificador ML.
"""

import os
import pandas as pd
from pathlib import Path

# Colores para terminal
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text):
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")


def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_error(text):
    print(f"{RED}❌ {text}{RESET}")


def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")


# Features requeridas por el modelo ML
REQUIRED_ML_FEATURES = [
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


def check_file_exists(filepath):
    """Verifica si un archivo existe"""
    return os.path.exists(filepath)


def check_csv_columns(filepath):
    """Lee las columnas de un CSV"""
    try:
        df = pd.read_csv(filepath, nrows=1)
        return list(df.columns)
    except Exception as e:
        return None


def main():
    print_header("DIAGNÓSTICO ML - EXOPLANET EXPLORER")

    base_dir = Path(__file__).parent
    ml_dir = base_dir / "ML"

    # 1. Verificar directorio ML
    print_header("1. VERIFICACIÓN DE DIRECTORIO")
    if ml_dir.exists():
        print_success(f"Directorio ML encontrado: {ml_dir}")
    else:
        print_error(f"Directorio ML no encontrado: {ml_dir}")
        return

    # 2. Verificar archivos CSV
    print_header("2. VERIFICACIÓN DE ARCHIVOS CSV")

    csv_files = {
        "exoplanets_visual.csv": ml_dir / "exoplanets_visual.csv",
        "koi_completo.csv": ml_dir / "koi_completo.csv",
        "exoplanets_clean.csv": ml_dir / "exoplanets_clean.csv",
    }

    available_csvs = {}
    for name, path in csv_files.items():
        if check_file_exists(path):
            print_success(f"{name} encontrado")
            available_csvs[name] = path
        else:
            print_warning(f"{name} NO encontrado")

    # 3. Verificar modelos ML
    print_header("3. VERIFICACIÓN DE MODELOS ML")

    model_files = {
        "Clasificador": ml_dir / "exoplanet_classifier.joblib",
        "Scaler": ml_dir / "scaler.joblib",
        "Label Encoder": ml_dir / "label_encoder.joblib",
    }

    models_ok = True
    for name, path in model_files.items():
        if check_file_exists(path):
            print_success(f"{name} encontrado")
        else:
            print_error(f"{name} NO encontrado")
            models_ok = False

    # 4. Analizar columnas de cada CSV
    print_header("4. ANÁLISIS DE COLUMNAS (FEATURES ML)")

    compatible_files = []

    for csv_name, csv_path in available_csvs.items():
        print(f"\n{BLUE}Analizando: {csv_name}{RESET}")
        columns = check_csv_columns(csv_path)

        if columns is None:
            print_error(f"Error al leer {csv_name}")
            continue

        print_info(f"Total de columnas: {len(columns)}")

        # Verificar features ML requeridas
        missing_features = []
        found_features = []

        for feature in REQUIRED_ML_FEATURES:
            if feature in columns:
                found_features.append(feature)
            else:
                missing_features.append(feature)

        print(
            f"  Features ML encontradas: {len(found_features)}/{len(REQUIRED_ML_FEATURES)}"
        )

        if len(missing_features) == 0:
            print_success(f"¡{csv_name} tiene TODAS las features necesarias!")
            compatible_files.append(csv_name)
        else:
            print_warning(f"{csv_name} le faltan {len(missing_features)} features:")
            for feat in missing_features[:5]:  # Mostrar solo las primeras 5
                print(f"    - {feat}")
            if len(missing_features) > 5:
                print(f"    ... y {len(missing_features) - 5} más")

    # 5. Recomendaciones
    print_header("5. DIAGNÓSTICO Y RECOMENDACIONES")

    if not models_ok:
        print_error("PROBLEMA: Faltan modelos ML")
        print_info(
            "SOLUCIÓN: Entrena el modelo ejecutando 'ML/ML.py' o coloca los archivos .joblib en la carpeta ML/"
        )
        print()

    if compatible_files:
        print_success(f"Archivos compatibles con ML: {', '.join(compatible_files)}")
        print_info(
            f"RECOMENDACIÓN: Usa '{compatible_files[0]}' para la predicción por lote"
        )

        # Mostrar instrucciones
        print(f"\n{GREEN}PARA HABILITAR COLORACIÓN POR CLASIFICACIÓN ML:{RESET}")
        print(f"  1. Carga la app: streamlit run streamlit_app.py")
        print(f"  2. Ve al 'Simulador 3D'")
        print(f"  3. Abre el expander 'Controles & Clasificador ML'")
        print(f"  4. Haz clic en 'Predecir clasificación ML para todo el dataset'")
        print(f"  5. Selecciona 'Clasificación ML' en el dropdown 'Colorear por:'")
    else:
        print_warning("PROBLEMA: Ningún CSV tiene las features ML necesarias")
        print_info("OPCIONES:")
        print(
            "  1. Usa 'koi_completo.csv' si lo tienes disponible (contiene todas las features)"
        )
        print("  2. Copia el archivo desde otra fuente de datos de Kepler")
        print(
            "  3. Usa el formulario individual para agregar exoplanetas con predicción"
        )

    # 6. Resumen de estado
    print_header("6. RESUMEN DE ESTADO")

    status = []
    if models_ok:
        status.append("✅ Modelos ML: OK")
    else:
        status.append("❌ Modelos ML: FALTA")

    if available_csvs:
        status.append(f"✅ Archivos CSV: {len(available_csvs)} encontrados")
    else:
        status.append("❌ Archivos CSV: NINGUNO")

    if compatible_files:
        status.append(f"✅ Compatibilidad ML: {len(compatible_files)} archivos")
    else:
        status.append("❌ Compatibilidad ML: NINGUNO")

    for s in status:
        print(s)

    print(f"\n{BLUE}{'=' * 60}{RESET}\n")

    if models_ok and compatible_files:
        print_success("¡TODO LISTO! Puedes usar la predicción ML por lote.")
        return 0
    else:
        print_warning(
            "Hay problemas que necesitan atención. Revisa las recomendaciones arriba."
        )
        return 1


if __name__ == "__main__":
    try:
        exit(main())
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
