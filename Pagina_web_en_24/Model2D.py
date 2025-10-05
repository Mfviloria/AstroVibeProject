import sys
import numpy as np
import pandas as pd
from vispy import scene, color
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont
import joblib

# --- Cargar modelo ML ---
model = joblib.load("ML/exoplanet_classifier.joblib")
encoder = joblib.load("ML/label_encoder.joblib")
scaler = joblib.load("ML/scaler.joblib")

# --- Cargar datos existentes ---
df = pd.read_csv("/Users/mariafernandaviloriazapata/Desktop/Pagina_web_en_24/exoplanets_visual.csv")
koi = pd.read_csv("/Users/mariafernandaviloriazapata/Desktop/Pagina_web_en_24/ML/koi_completo.csv")
koi_ex = koi.to_dict(orient="records")
koi_dict = {str(k['kepoi_name']): k for k in koi_ex}
exoplanetas = df.to_dict(orient="records")

# Convertir KOI a diccionario rápido
koi_ex = koi.to_dict(orient="records")
koi_dict = {str(k['kepoi_name']): k for k in koi_ex}
# --- Preparar datos de exoplanetas ---
xs, ys, sizes, colors_vals, nombres = [], [], [], [], []
clasf, temperture, radio, Orbit, transitD, StellarT, transitDepth, SSG, Sr, TransitE = [], [], [], [], [], [], [], [], [], []

for planeta in exoplanetas:
    try:
        x0 = (planeta["ra"] - df["ra"].min()) / (df["ra"].max() - df["ra"].min())
        y0 = (planeta["dec"] - df["dec"].min()) / (df["dec"].max() - df["dec"].min())
    except:
        continue

    # Radio y color
    tamaño = max(2, min(10, planeta.get("pl_rade", 2)))
    eqt = planeta.get("pl_eqt", np.nan)
    if np.isnan(eqt):
        eqt = 0

    # Guardar valores
    xs.append(x0)
    ys.append(y0)
    sizes.append(tamaño)
    colors_vals.append(eqt)
    nombres.append(planeta.get("hostname", "Desconocido"))

    # Información KOI
    nombre = str(planeta["hostname"])
    if nombre in koi_dict:
        k = koi_dict[nombre]
        clasf.append(k.get('koi_disposition', 'Desconocida'))
        temperture.append(k.get('koi_teq', np.nan))
        radio.append(k.get('koi_prad', np.nan))
        Orbit.append(k.get('koi_sma', np.nan))
        transitD.append(k.get('koi_duration', np.nan))
        StellarT.append(k.get('koi_steff', np.nan))
        transitDepth.append(k.get('koi_depth', np.nan))
        SSG.append(k.get('koi_slogg', np.nan))
        Sr.append(k.get('koi_srad', np.nan))
        TransitE.append(k.get('koi_time0bk', np.nan))
    else:
        clasf.append('Desconocida')
        temperture.append(np.nan)
        radio.append(np.nan)
        Orbit.append(np.nan)
        transitD.append(np.nan)
        StellarT.append(np.nan)
        transitDepth.append(np.nan)
        SSG.append(np.nan)
        Sr.append(np.nan)
        TransitE.append(np.nan)

# --- Convertir a NumPy ---
xs = np.array(xs)
ys = np.array(ys)
sizes = np.array(sizes)
colors_vals = np.array(colors_vals)
nombres = np.array(nombres)

# --- Normalizar colores ---
if len(colors_vals) > 0 and colors_vals.max() != colors_vals.min():
    colors_norm = (colors_vals - colors_vals.min()) / (colors_vals.max() - colors_vals.min())
else:
    colors_norm = np.ones_like(colors_vals) * 0.5  # color medio si no hay rango

cmap = color.get_colormap("plasma")
colors_rgba = np.array([cmap.map(c)[0] for c in colors_norm])

# --- Verificación rápida ---
print(f"Exoplanetas cargados: {len(xs)}")
print(f"Primeros 5 colores: {colors_vals[:5]}")

# --- Aplicación PyQt ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exoplanetas 2D con Resalte")
        self.resize(1600, 900)

        layout = QHBoxLayout(self)

        # --- Panel de inputs ---
        self.form_layout = QFormLayout()
        self.inputs = {}
        fields = [
            "Nombre", "RA (0-360)", "Dec (-90 a 90)", "Radio R⊕", "Temperatura K",
            "Transit Signal-to-Noise", "Orbit Semi-major Axis [au]", "Orbital Period [days]",
            "Transit Duration [hrs]", "Stellar Effective Temperature [K]", "Transit Depth [ppm]",
            "Stellar Surface Gravity [log10(cm/s**2)]", "Stellar Radius [Solar radii]", "Transit Epoch [BKJD]"
        ]
        for f in fields:
            self.inputs[f] = QLineEdit()
            self.form_layout.addRow(f+":", self.inputs[f])

        # Botón agregar
        self.add_button = QPushButton("Agregar Exoplaneta")
        self.form_layout.addRow(self.add_button)

        # Label de info debajo
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont("Arial", 11))
        self.form_layout.addRow(self.info_label)

        layout.addLayout(self.form_layout)

        # --- Canvas VisPy ---
        self.canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='black', size=(1200, 800))
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.PanZoomCamera(aspect=1, interactive=True)
        layout.addWidget(self.canvas.native)

        # --- Scatter de exoplanetas ---
        self.scatter = scene.visuals.Markers()
        self.scatter.set_data(np.c_[xs, ys], face_color=colors_rgba, size=sizes*5)
        self.view.add(self.scatter)

        # --- Halo de resaltado ---
        self.halo = scene.visuals.Markers()
        self.halo.set_data(np.array([[0,0]]), face_color=(1,1,0,0.4), size=0)
        self.view.add(self.halo)
        self.halo_pulse = 0
        self.pulse_dir = 1
        self.highlight_idx = None
        self.new_idx = None

        # --- Conexiones ---
        self.add_button.clicked.connect(self.on_add_clicked)
        self.canvas.events.draw.connect(self.update_halo)
        self.canvas.events.mouse_double_click.connect(self.on_double_click)

    def center_camera(self, x, y, zoom=1.5):
        width = 1.0 / zoom
        height = width * (self.canvas.size[1]/self.canvas.size[0])
        self.view.camera.rect = (x - width/2, y - height/2, width, height)

    def on_add_clicked(self):
        global xs, ys, sizes, colors_rgba, nombres

        # Obtener datos del input
        try:
            name = self.inputs["Nombre"].text()
            ra = float(self.inputs["RA (0-360)"].text())
            dec = float(self.inputs["Dec (-90 a 90)"].text())
            rade = float(self.inputs["Radio R⊕"].text())
            eqt = float(self.inputs["Temperatura K"].text())
            snr = float(self.inputs["Transit Signal-to-Noise"].text())
            sma = float(self.inputs["Orbit Semi-major Axis [au]"].text())
            period = float(self.inputs["Orbital Period [days]"].text())
            dur = float(self.inputs["Transit Duration [hrs]"].text())
            steff = float(self.inputs["Stellar Effective Temperature [K]"].text())
            depth = float(self.inputs["Transit Depth [ppm]"].text())
            slogg = float(self.inputs["Stellar Surface Gravity [log10(cm/s**2)]"].text())
            StellarR = float(self.inputs["Stellar Radius [Solar radii]"].text())
            time0bk = float(self.inputs["Transit Epoch [BKJD]"].text())
            
            datos = np.array([[snr, rade, sma, eqt, period, dur, depth, steff, slogg, StellarR, time0bk]])
            nuevo_exoplaneta_s = scaler.transform(datos)
            prediccion = model.predict(nuevo_exoplaneta_s)
            resultado = encoder.inverse_transform(prediccion)
        except ValueError:
            self.info_label.setText("Error: ingresa valores numéricos correctos")
            return

        # Revisar si ya existe
        if name in nombres:
            idx = np.where(nombres == name)[0][0]
            self.highlight_idx = idx
            self.new_idx = None
            self.center_camera(xs[idx], ys[idx])
            self.info_label.setText(f"¡El exoplaneta '{name}' ya existe!\nRadio: {sizes[idx]:.2f} R⊕\nTemperatura: {colors_vals[idx]:.0f} K\nClasificación: {resultado[0]}")
            return

        # Normalizar coordenadas
        x0 = (ra - df["ra"].min()) / (df["ra"].max() - df["ra"].min())
        y0 = (dec - df["dec"].min()) / (df["dec"].max() - df["dec"].min())

        xs = np.append(xs, x0)
        ys = np.append(ys, y0)
        sizes = np.append(sizes, max(2, min(10, rade)))
        nombres = np.append(nombres, name)

        norm_color = (eqt - colors_vals.min()) / (colors_vals.max() - colors_vals.min())
        color_val = cmap.map(norm_color)[0]
        colors_rgba = np.vstack([colors_rgba, color_val])

        self.scatter.set_data(np.c_[xs, ys], face_color=colors_rgba, size=sizes*5)

        self.new_idx = len(xs)-1
        self.highlight_idx = None
        self.center_camera(x0, y0)
        self.info_label.setText(f"Nuevo exoplaneta:\nNombre: {name}\nRadio: {rade:.2f} R⊕\nTemperatura: {eqt:.0f} K\nClasificación: {resultado[0]}")

    def on_double_click(self, event):
        if event.pos is None or len(xs) == 0:
            return
        pos = self.view.scene.transform.imap(event.pos)[:2]
        dists = np.hypot(xs - pos[0], ys - pos[1])
        idx = np.argmin(dists)
        if dists[idx] < 0.02:
            self.highlight_idx = idx
            self.new_idx = None
            self.center_camera(xs[idx], ys[idx])

            info_text = (
                f"Seleccionado:\n"
                f"Nombre: {nombres[idx]}\n"
                f"Radio: {sizes[idx]:.2f} R⊕\n"
                f"Temperatura: {colors_vals[idx]:.0f} K\n"
                f"Clasificación KOI: {clasf[idx]}\n"
                f"Radio KOI: {radio[idx]:.2f} R⊕\n"
                f"Órbita: {Orbit[idx]:.2f} au\n"
                f"Periodo orbital: {TransitE[idx]:.2f} días\n"
                f"Duración del tránsito: {transitD[idx]:.2f} hrs\n"
                f"Profundidad del tránsito: {transitDepth[idx]:.2f} ppm\n"
                f"Temperatura estelar: {StellarT[idx]:.0f} K\n"
                f"Gravedad superficial estelar: {SSG[idx]:.2f} log10(cm/s²)\n"
                f"Radio estelar: {Sr[idx]:.2f} R☉\n"
            )
            self.info_label.setText(info_text)


    def update_halo(self, event):
        idx = self.new_idx if self.new_idx is not None else self.highlight_idx
        if idx is not None:
            self.halo_pulse += self.pulse_dir * 0.05
            if self.halo_pulse > 1 or self.halo_pulse < 0:
                self.pulse_dir *= -1
            halo_size = sizes[idx]*8*(1 + 0.3*self.halo_pulse)
            self.halo.set_data(np.array([[xs[idx], ys[idx]]]),
                               face_color=(1,1,0,0.4),
                               size=halo_size)
        else:
            self.halo.set_data(np.array([[0,0]]), size=0)

if __name__ == "__main__":
    app_qt = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app_qt.exec_())
