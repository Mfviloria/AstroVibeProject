# 🚀 Deployment Guide - Exoplanet Explorer

Complete step-by-step guide to deploy your Streamlit app to the cloud.

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Repository Setup](#repository-setup)
3. [Deploy to Streamlit Cloud](#deploy-to-streamlit-cloud)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [Troubleshooting](#troubleshooting)
6. [Alternative Deployment Options](#alternative-deployment-options)

---

## ✅ Prerequisites

Before deploying, make sure you have:

- [x] GitHub account
- [x] Git installed on your computer
- [x] All changes committed and pushed to GitHub
- [x] `requirements.txt` with all dependencies
- [x] `.streamlit/config.toml` configuration file
- [x] Data files in `ML/` directory (at least `exoplanets_visual.csv`)

---

## 🔧 Repository Setup

### 1. Verify Your Repository

Your code is already pushed to:
```
https://github.com/Mfviloria/AstroVibeProject.git
Branch: main
```

### 2. Check Required Files

Make sure these files exist:
```
AstroVibeProject/
└── Pagina_web_en_24/
    ├── streamlit_app.py          ✅ Main app file
    ├── requirements.txt           ✅ Dependencies
    ├── .streamlit/
    │   └── config.toml           ✅ Configuration
    ├── style.css                  ✅ Custom styling
    ├── ML/
    │   ├── exoplanets_visual.csv ✅ Data file
    │   ├── koi_completo.csv      ✅ ML data (optional)
    │   └── *.joblib              ⚠️ ML models (optional)
    └── README_STREAMLIT.md        ✅ Documentation
```

---

## 🌐 Deploy to Streamlit Cloud

### Step 1: Access Streamlit Cloud

1. Open your browser and go to: **https://share.streamlit.io**

2. Click **"Sign in"** or **"Get started"**

3. Choose **"Continue with GitHub"**

4. Authorize Streamlit to access your GitHub account

### Step 2: Create New App

1. Once logged in, click the **"New app"** button (top right)

2. You'll see a form with these fields:

   **Repository:**
   ```
   Mfviloria/AstroVibeProject
   ```

   **Branch:**
   ```
   main
   ```

   **Main file path:**
   ```
   Pagina_web_en_24/streamlit_app.py
   ```

   **App URL (optional):**
   ```
   exoplanet-explorer  (or your preferred name)
   ```

3. Click **"Deploy!"**

### Step 3: Wait for Deployment

The deployment process will:
- ✓ Clone your repository
- ✓ Install Python dependencies from `requirements.txt`
- ✓ Start the Streamlit server
- ✓ Generate a public URL

**Estimated time:** 2-5 minutes

### Step 4: Access Your App

Once deployed, you'll get a URL like:
```
https://exoplanet-explorer.streamlit.app
```

Or:
```
https://your-username-appname-hash.streamlit.app
```

---

## ⚙️ Post-Deployment Configuration

### Custom Domain (Optional)

1. Go to your app dashboard on Streamlit Cloud
2. Click **Settings** → **General**
3. Under "App URL", customize your subdomain
4. Click **Save**

### Secrets Management (If Needed)

If you need API keys or passwords:

1. Go to your app dashboard
2. Click **Settings** → **Secrets**
3. Add your secrets in TOML format:
   ```toml
   # Example
   [api_keys]
   openai = "your-api-key-here"
   ```
4. Access in code with:
   ```python
   import streamlit as st
   api_key = st.secrets["api_keys"]["openai"]
   ```

### Resource Settings

1. Go to **Settings** → **Resources**
2. Default settings are usually fine:
   - **CPU:** 0.078 cores
   - **Memory:** 800 MB
   - **Disk:** 3 GB

### Reboot App

If your app has issues:
1. Go to your app dashboard
2. Click the **⋮** menu (three dots)
3. Select **"Reboot app"**

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. "No module named 'X'" Error

**Problem:** Missing dependency

**Solution:**
```bash
# Add to requirements.txt
echo "missing-package-name" >> Pagina_web_en_24/requirements.txt
git add Pagina_web_en_24/requirements.txt
git commit -m "Add missing dependency"
git push origin main
```

Streamlit will automatically redeploy.

#### 2. "File not found" Error

**Problem:** Data files not in repository

**Solution:**
- Make sure `ML/exoplanets_visual.csv` is committed
- Check file paths are relative, not absolute
- Verify case-sensitivity in file names

#### 3. App Crashes on Startup

**Problem:** Error in code or configuration

**Solution:**
1. Check logs in Streamlit Cloud dashboard
2. Click **"Manage app"** → **"Logs"**
3. Look for Python errors
4. Fix locally and push to GitHub

#### 4. Slow Performance

**Problem:** Large dataset or inefficient code

**Solution:**
- Use `@st.cache_data` decorator for data loading
- Reduce dataset size
- Optimize calculations

**Example:**
```python
@st.cache_data
def load_data():
    return pd.read_csv('ML/exoplanets_visual.csv')
```

#### 5. App Shows Old Version

**Problem:** Cache not cleared

**Solution:**
1. Go to app dashboard
2. Click **"Clear cache"**
3. Click **"Reboot app"**

---

## 🔄 Update Your Deployed App

After making changes locally:

```bash
# 1. Make your changes
# 2. Test locally
streamlit run streamlit_app.py

# 3. Commit changes
git add .
git commit -m "Description of changes"

# 4. Push to GitHub
git push origin main

# 5. Streamlit Cloud will automatically redeploy (takes 1-2 minutes)
```

---

## 🌍 Alternative Deployment Options

### Option 1: Hugging Face Spaces

1. Go to https://huggingface.co/spaces
2. Create new Space
3. Choose "Streamlit" as SDK
4. Upload your files or connect GitHub
5. Add `requirements.txt` and `app.py` (rename from streamlit_app.py)

### Option 2: Heroku

```bash
# Install Heroku CLI
# Create Procfile
echo "web: streamlit run streamlit_app.py --server.port=$PORT" > Procfile

# Create setup.sh
cat > setup.sh << 'EOF'
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
EOF

# Deploy
heroku create your-app-name
git push heroku main
```

### Option 3: AWS (Advanced)

- Use EC2 instance
- Install Docker
- Deploy with Docker container
- Configure security groups and load balancer

### Option 4: Local Server (Development Only)

```bash
# Run on local network
streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=8501
```

---

## 📊 Monitoring Your App

### View Analytics

1. Go to Streamlit Cloud dashboard
2. Click your app
3. View **Analytics** tab to see:
   - Number of visitors
   - Session duration
   - Geographic distribution

### Check Logs

1. Click **"Manage app"**
2. Select **"Logs"** tab
3. Monitor real-time app behavior
4. Debug errors

### Resource Usage

1. Go to **Settings** → **Resources**
2. Monitor CPU and memory usage
3. Upgrade plan if needed

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] App loads without errors
- [ ] 2D Simulator displays correctly
- [ ] 3D Simulator renders properly
- [ ] Assistant chatbot responds
- [ ] Data files are accessible
- [ ] Forms work correctly
- [ ] Predictions run (if ML models available)
- [ ] Mobile responsiveness
- [ ] Custom styling applies
- [ ] Share URL with others

---

## 📞 Support Resources

### Streamlit Documentation
- https://docs.streamlit.io/streamlit-community-cloud

### Community Forum
- https://discuss.streamlit.io

### GitHub Issues
- https://github.com/Mfviloria/AstroVibeProject/issues

---

## 🎓 Best Practices

1. **Always test locally first** before pushing to production
2. **Use version control** with meaningful commit messages
3. **Keep secrets secure** - never commit API keys
4. **Monitor logs** regularly for errors
5. **Optimize performance** with caching
6. **Document changes** in commit messages
7. **Keep dependencies updated** but test compatibility
8. **Backup your data** files separately

---

## 🚀 Your App is Live!

Congratulations! Your Exoplanet Explorer app is now accessible worldwide.

**Share your app:**
- Copy the URL from Streamlit Cloud
- Share on social media
- Add to your portfolio
- Include in README

**Example URL:**
```
https://exoplanet-explorer.streamlit.app
```

---

**Built with ❤️ using Streamlit Cloud**

**Last Updated:** 2024

**Questions?** Open an issue on GitHub or ask the community!