# 🎨 Guía: Coloración por Clasificación ML en el Simulador 3D

## 📋 Tabla de Contenidos
1. [Introducción](#introducción)
2. [¿Por qué no funciona inicialmente?](#por-qué-no-funciona-inicialmente)
3. [Paso a paso: Cómo habilitar la coloración ML](#paso-a-paso-cómo-habilitar-la-coloración-ml)
4. [Archivos de datos disponibles](#archivos-de-datos-disponibles)
5. [Solución de problemas](#solución-de-problemas)
6. [Información técnica](#información-técnica)

---

## 🎯 Introducción

La funcionalidad de **Coloración por Clasificación ML** permite visualizar los exoplanetas en el simulador 3D con diferentes colores según su clasificación predicha por un modelo de Machine Learning.

Cada color representa una categoría diferente (por ejemplo: "CONFIRMED", "CANDIDATE", "FALSE POSITIVE"), lo que facilita la identificación visual de grupos de exoplanetas con características similares.

---

## ❓ ¿Por qué no funciona inicialmente?

La coloración por clasificación ML requiere **dos condiciones** que deben cumplirse:

### 1️⃣ Dataset con features ML completas
El archivo CSV debe contener **11 columnas específicas** necesarias para el modelo:
- `koi_model_snr` - Transit Signal-to-Noise
- `koi_prad` - Planetary Radius
- `koi_sma` - Orbit Semi-Major Axis
- `koi_teq` - Equilibrium Temperature
- `koi_period` - Orbital Period
- `koi_duration` - Transit Duration
- `koi_depth` - Transit Depth
- `koi_steff` - Stellar Effective Temperature
- `koi_slogg` - Stellar Surface Gravity
- `koi_srad` - Stellar Radius
- `koi_time0bk` - Transit Epoch

### 2️⃣ Predicciones generadas
Una vez cargado el dataset correcto, debes ejecutar la predicción por lote para generar la columna `pred_class` con las clasificaciones.

**PROBLEMA COMÚN:** El archivo `exoplanets_visual.csv` NO contiene estas columnas, solo tiene datos básicos de visualización (ra, dec, pl_name, etc.).

---

## 🚀 Paso a paso: Cómo habilitar la coloración ML

### Método Recomendado: Usar koi_completo.csv

#### **Paso 1: Verificar archivos disponibles** ✅
Ejecuta el script de diagnóstico:
```bash
python diagnostico_ml.py
```

Este script te dirá:
- ✅ Qué archivos CSV tienes
- ✅ Cuáles son compatibles con ML
- ✅ Si los modelos ML están presentes

#### **Paso 2: Cargar la aplicación** 🖥️
```bash
streamlit run streamlit_app.py
```

#### **Paso 3: Ir al Simulador 3D** 🌌
En el menú lateral, selecciona **"Simulador 3D"**

#### **Paso 4: Seleccionar el archivo correcto** 📂
En la sidebar, bajo **"📂 Fuente de Datos"**:
1. Abre el dropdown "Selecciona el archivo CSV a cargar:"
2. Selecciona: **"koi_completo.csv (✅ ML completo)"**
3. Haz clic en **"🔄 Recargar datos desde archivo"**

Deberías ver el mensaje: ✅ Cargado: [número] exoplanetas

#### **Paso 5: Ejecutar predicción por lote** 🤖
1. Abre el expander **"Controles & Clasificador ML"** en la sidebar
2. Verás el mensaje: "ℹ️ **Casi listo para ML** - Dataset compatible"
3. Haz clic en el botón: **"Predecir clasificación ML para todo el dataset"**
4. Espera unos segundos mientras procesa
5. Verás: ✅ Predicción por lote completada: columna 'pred_class' añadida

#### **Paso 6: Activar coloración por clasificación** 🎨
1. En el mismo expander "Controles & Clasificador ML"
2. Busca el dropdown **"Colorear por:"**
3. Selecciona: **"Clasificación ML"**

¡Listo! Ahora el gráfico 3D mostrará los exoplanetas coloreados por su clasificación ML.

---

## 📊 Archivos de datos disponibles

### ✅ koi_completo.csv (RECOMENDADO para ML)
- **Ubicación:** `ML/koi_completo.csv`
- **Columnas:** ~155 columnas totales
- **Features ML:** ✅ LAS 11 NECESARIAS
- **Origen:** Kepler Objects of Interest - NASA
- **Uso:** Predicción ML por lote + Visualización 3D
- **Tamaño:** Grande (~9000+ exoplanetas candidatos)

### ⚠️ exoplanets_visual.csv (Solo visualización)
- **Ubicación:** `ML/exoplanets_visual.csv`
- **Columnas:** ~14 columnas básicas
- **Features ML:** ❌ NINGUNA
- **Uso:** Solo visualización 3D
- **Limitaciones:** NO permite predicción por lote
- **Alternativa:** Usa formulario individual para predicción

### 📁 exoplanets_visual.csv (Proyecto NASA)
- **Ubicación:** `proyecto nasa/exoplanets_visual.csv`
- **Similar a:** exoplanets_visual.csv (ML)
- **Features ML:** ❌ NINGUNA
- **Uso:** Solo visualización 3D

---

## 🔧 Solución de problemas

### Problema 1: "Clasificación ML (No disponible)" en el dropdown
**Causa:** No hay clasificaciones generadas o el dataset no tiene features ML.

**Solución:**
1. Verifica que estés usando `koi_completo.csv`
2. Ejecuta "Predecir clasificación ML para todo el dataset"
3. Si sigue sin funcionar, recarga la página

---

### Problema 2: Botón de predicción por lote no aparece
**Causa:** El dataset no tiene las 11 features necesarias.

**Solución:**
```
1. Abre selector "Fuente de Datos" (sidebar)
2. Cambia a "koi_completo.csv (✅ ML completo)"
3. Haz clic en "🔄 Recargar datos desde archivo"
4. Verifica el mensaje: "ℹ️ Casi listo para ML"
```

---

### Problema 3: "Dataset no contiene las features necesarias"
**Causa:** Estás usando `exoplanets_visual.csv` que solo tiene datos básicos.

**Solución:**
Cambia a `koi_completo.csv` siguiendo los pasos del **Paso 4** arriba.

---

### Problema 4: Los puntos aparecen pero sin colores distintos
**Causa:** Todos los exoplanetas tienen la misma clasificación, o hay un error en la predicción.

**Solución:**
1. Verifica el mensaje: "🎨 Coloreando por Clasificación ML - X exoplanetas clasificados en Y categorías"
2. Si dice "1 categoría", es normal que todos tengan el mismo color
3. Revisa si los modelos ML están entrenados correctamente

---

### Problema 5: Error al cargar koi_completo.csv
**Causa:** Archivo muy grande o memoria insuficiente.

**Solución:**
```python
# Opción: Crear un subset más pequeño
import pandas as pd
df = pd.read_csv("ML/koi_completo.csv", nrows=1000)  # Solo 1000 filas
df.to_csv("ML/koi_sample.csv", index=False)
```
Luego carga `koi_sample.csv` en lugar del completo.

---

## 🔬 Información técnica

### Arquitectura del sistema

```
┌─────────────────────────────────────┐
│  1. Selector de Archivo (Sidebar)  │
│     - koi_completo.csv              │
│     - exoplanets_visual.csv         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. Carga y Mapeo de Columnas      │
│     - Lectura del CSV               │
│     - Mapeo koi_* → pl_*            │
│     - Validación de columnas        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3. Verificación de Features ML    │
│     - Buscar 11 features requeridas │
│     - Habilitar/deshabilitar botón  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  4. Predicción por Lote (Opcional)  │
│     - Cargar modelos (.joblib)      │
│     - Transformar con scaler        │
│     - Predecir con clasificador     │
│     - Decodificar con encoder       │
│     - Agregar columna pred_class    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  5. Visualización 3D                │
│     - Selector de modo de color     │
│     - Temperatura: colorscale       │
│     - Clasificación: color por cat. │
└─────────────────────────────────────┘
```

### Modelos ML requeridos

Los siguientes archivos deben estar en `ML/`:
- `exoplanet_classifier.joblib` - Modelo entrenado (RandomForest, etc.)
- `scaler.joblib` - StandardScaler para normalización
- `label_encoder.joblib` - LabelEncoder para categorías

### Columnas generadas

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `pred_class` | string | Clasificación predicha (CONFIRMED, CANDIDATE, FALSE POSITIVE) |

### Mapeo de columnas KOI → Visualización

Cuando se carga `koi_completo.csv`, se realiza este mapeo automático:

| Columna KOI | Columna Visualización | Propósito |
|-------------|----------------------|-----------|
| `kepoi_name` | `pl_name` | Nombre del planeta |
| `kepoi_name` | `hostname` | Nombre del sistema |
| `koi_prad` | `pl_rade` | Radio planetario |
| `koi_teq` | `pl_eqt` | Temperatura equilibrio |
| `koi_period` | `pl_orbper` | Período orbital |
| `koi_steff` | `st_teff` | Temperatura estelar |

---

## 📞 Soporte

Si tienes problemas:

1. **Ejecuta el diagnóstico:**
   ```bash
   python diagnostico_ml.py
   ```

2. **Pregunta al asistente virtual:**
   - En la sidebar, abre "Asistente para principiantes 🤖"
   - Escribe: "¿Por qué no funciona la coloración por clasificación?"
   - O: "¿Cómo cargo koi_completo.csv?"

3. **Verifica los archivos:**
   ```bash
   ls -lh ML/
   # Deberías ver:
   # - koi_completo.csv
   # - exoplanet_classifier.joblib
   # - scaler.joblib
   # - label_encoder.joblib
   ```

---

## 🎓 Conclusión

La coloración por clasificación ML es una herramienta poderosa para explorar patrones en los datos de exoplanetas. La clave es:

1. ✅ Usar el archivo correcto (`koi_completo.csv`)
2. ✅ Ejecutar la predicción por lote
3. ✅ Seleccionar "Clasificación ML" en el dropdown

¡Disfruta explorando el universo de exoplanetas! 🌌🪐