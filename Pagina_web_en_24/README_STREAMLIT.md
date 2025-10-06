# 🌌 Exoplanet Explorer - Streamlit App

An interactive web application for exploring and classifying exoplanets in 2D and 3D visualizations, powered by Machine Learning.

![Streamlit](https://img.shields.io/badge/Streamlit-1.50.0-FF4B4B?style=for-the-badge&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## 🚀 Features

### 📊 2D Simulator
- Interactive 2D visualization of exoplanets based on RA/Dec coordinates
- Add new exoplanets with custom parameters
- Real-time ML predictions for exoplanet classification
- Color-coded temperature visualization
- Hover tooltips with detailed information

### 🌐 3D Simulator
- Immersive 3D space visualization using Plotly
- Distance units: parsecs (pc), light-years (ly), or astronomical units (au)
- Search and highlight specific exoplanets
- Dynamic camera positioning and zoom controls
- Starfield background for enhanced depth perception
- Color by temperature or ML classification

### 🤖 ML Classifier
- Predict exoplanet classification using trained models
- Batch prediction for entire datasets
- Individual prediction form for custom inputs
- 11 features support: SNR, radius, semi-major axis, temperature, period, duration, depth, stellar parameters

### 💬 Beginner's Assistant
- Interactive AI assistant for help and guidance
- Context-aware responses
- Explanations about exoplanets and detection methods
- Step-by-step instructions

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/Mfviloria/AstroVibeProject.git
cd AstroVibeProject/Pagina_web_en_24
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
streamlit run streamlit_app.py
```

5. **Open your browser**
The app will automatically open at `http://localhost:8501`

## 📦 Required Files

Make sure these files are in the `ML/` directory:

### Data Files
- `exoplanets_visual.csv` - Main dataset for visualization
- `koi_completo.csv` - Complete Kepler dataset with all ML features

### ML Model Files (optional, for predictions)
- `exoplanet_classifier.joblib` - Trained classifier model
- `scaler.joblib` - Feature scaler
- `label_encoder.joblib` - Label encoder for classifications

## 🌐 Deploy to Streamlit Cloud

### Step 1: Prepare Your Repository

1. **Commit your changes**
```bash
git add .
git commit -m "Prepare app for Streamlit Cloud deployment"
git push origin main
```

2. **Verify requirements.txt** includes all dependencies

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `Mfviloria/AstroVibeProject`
5. Set branch: `main` (or your preferred branch)
6. Set main file path: `Pagina_web_en_24/streamlit_app.py`
7. Click "Deploy!"

### Step 3: Configuration (Optional)

If needed, you can add environment variables in the Streamlit Cloud dashboard:
- Settings → Secrets → Add your variables

## 📁 Project Structure

```
Pagina_web_en_24/
├── streamlit_app.py           # Main application file
├── requirements.txt            # Python dependencies
├── style.css                   # Custom CSS styling
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── ML/
│   ├── exoplanets_visual.csv  # Visualization dataset
│   ├── koi_completo.csv       # Complete ML dataset
│   ├── exoplanet_classifier.joblib
│   ├── scaler.joblib
│   └── label_encoder.joblib
├── diagnostico_ml.py          # ML diagnostics tool
└── README_STREAMLIT.md        # This file
```

## 🎮 How to Use

### 2D Simulator
1. Navigate to "2D Simulator" from the sidebar
2. View the scatter plot of exoplanets
3. Use the slider to adjust point sizes
4. Click "Add new exoplanet" to add custom entries
5. Select an exoplanet to view detailed information

### 3D Simulator
1. Navigate to "3D Simulator" from the sidebar
2. Choose units (pc, ly, or au)
3. Use mouse to rotate, zoom, and pan the 3D view
4. Search for specific exoplanets by name
5. Adjust point size scale with the slider
6. Use "Controls & ML Classifier" to run batch predictions

### ML Classifier
1. Go to "ML Classifier" section
2. Enter the 11 required features
3. Click "Predict class" to get the classification
4. Results will show: CONFIRMED, CANDIDATE, or FALSE POSITIVE

### Assistant
1. Expand "Beginner's Assistant 🤖" in the sidebar
2. Type your question in the input field
3. Click "Send question"
4. View the conversation history and responses

## 🔧 Troubleshooting

### "No data to display in 3D"
- Ensure `exoplanets_visual.csv` or `koi_completo.csv` exists in the `ML/` folder
- Check file permissions
- Verify CSV format is correct

### "ML model not found"
- Download or train the ML models
- Place `.joblib` files in the `ML/` folder
- Run `diagnostico_ml.py` to verify setup

### Performance Issues
- Reduce dataset size for faster loading
- Use smaller point sizes in visualizations
- Close other browser tabs

## 📊 Dataset Information

### exoplanets_visual.csv
- **Columns:** pl_name, hostname, ra, dec, pl_rade, pl_eqt, st_teff, sy_dist
- **Source:** NASA Exoplanet Archive
- **Use:** 2D and 3D visualization

### koi_completo.csv
- **Columns:** 155+ columns including all ML features
- **Source:** Kepler Mission (KOI - Kepler Objects of Interest)
- **Use:** ML predictions and complete analysis

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- **Maria Fernanda Viloria Zapata** - Initial work - [Mfviloria](https://github.com/Mfviloria)

## 🙏 Acknowledgments

- NASA Exoplanet Archive for the data
- Kepler Mission for KOI catalog
- Streamlit team for the amazing framework
- Plotly for interactive visualizations

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Streamlit**

🌟 If you find this project useful, please give it a star on GitHub!