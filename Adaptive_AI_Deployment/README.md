# 🧠 Adaptive AI Therapy - Startup Manual

This manual explains how to get the project up and running if you return to it after a long break.

## 📋 Prerequisites
Ensure you have Python installed on your system. This project uses a Virtual Environment (`venv`) to manage dependencies.

---

## 🚀 Quick Start (Step-by-Step)

### 1. Open a Terminal
Open your terminal (PowerShell or Command Prompt) and navigate to the project root:
`cd "c:\Users\- MD -\Documents\Adaptive_AI\Adaptive_AI_Deployment"`

### 2. Activate the Environment
You must use the virtual environment so the imports work correctly.
- **PowerShell**: `.\venv\Scripts\Activate.ps1`
- **CMD**: `.\venv\Scripts\activate.bat`

### 3. Start the Backend API
The frontend depends on this. Run it in a separate terminal window (make sure to activate venv there too):
`python backend/app.py`
*The server will start at http://127.0.0.1:5000*

### 4. Start the Dashboard (Frontend)
Run this in another terminal window (with venv activated):
`streamlit run ui/dashboard.py`
*The dashboard will open automatically in your browser at http://localhost:8501*

---

## 🛠 Troubleshooting

### "ModuleNotFoundError"
If you see Errors about missing modules (like `flask` or `streamlit`), ensure your `venv` is active. If it is active and still failing, reinstall dependencies:
`pip install -r backend/requirements.txt`

### Connection Error
If the Dashboard shows a "Connection Error", it means the **Backend API** is not running. Make sure you performed Step 3 above.

### Camera Not Found
The facial analysis requires a webcam. If you don't have one, you can disable "Facial Analysis" in the dashboard settings sidebar.

---

## 📁 Project Structure
- `backend/`: Flask API and core logic.
- `ui/`: Streamlit dashboard and styling.
- `models/`: Emotion detection modules (Text & Face).
- `rl_engine/`: Therapy recommendation logic.
- `venv/`: Python virtual environment.
