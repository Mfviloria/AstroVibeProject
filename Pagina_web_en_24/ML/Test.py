import numpy as np
import joblib

model = joblib.load("exoplanet_classifier.joblib")
encoder = joblib.load("label_encoder.joblib")
scaler = joblib.load("scaler.joblib")

# Orden: koi_model_snr[Transit Signal-to-Noise], koi_prad[Planetary Radius], koi_sma[Orbit Semi-Major Axis [au]], koi_teq[Equilibrium Temperature [K]], koi_period[Orbital Period [days]],
#        koi_duration[Transit Duration [hrs]], koi_depth[Transit Depth [ppm]], koi_steff[Stellar Effective Temperature [K]], koi_slogg[Stellar Surface Gravity [log10(cm/s**2)]], koi_srad[Stellar Radius [Solar radii]], koi_time0bk[Transit Epoch [BKJD]]
datos = np.array([[18.0, 0.59, 0.0739, 443, 10.3128, 3.2, 0.45, 5600, 4.4, 0.98, 2459000.123]])

nuevo_exoplaneta_s = scaler.transform(datos)

prediccion = model.predict(nuevo_exoplaneta_s)
resultado = encoder.inverse_transform(prediccion)

print("Clasificación del exoplaneta:", resultado[0])
