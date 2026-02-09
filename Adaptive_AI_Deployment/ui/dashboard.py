import sys
import os
import time
import streamlit as st
import requests

# =====================================================
# PROJECT PATH FIX
# =====================================================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# CONFIGURATION
# =====================================================
API_URL = "http://127.0.0.1:5000/analyze"

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Adaptive AI Therapy",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS (Glassmorphism & Modern UI)
# =====================================================
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Background with animated gradient */
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Glassmorphism Containers */
    .glass-container {
        background: rgba(255, 255, 255, 0.25);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 2rem;
        margin-bottom: 2rem;
    }

    /* Section Headers */
    h1, h2, h3 {
        color: white;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    p, label {
        color: #f0f0f0;
        font-weight: 400;
    }

    /* Input Area */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.9);
        border: none;
        border-radius: 12px;
        padding: 1rem;
        font-size: 1rem;
        color: #333;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTextArea textarea:focus {
        box-shadow: 0 0 0 2px #fff;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 30px rgba(0,0,0,0.3);
    }

    /* Result Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-label {
        color: #718096;
        font-size: 0.85rem;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 0.5rem;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #2d3748;
        font-size: 1.4rem;
        font-weight: 800;
    }

    /* Therapy Recommendation */
    .therapy-box {
        background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
        padding: 2.5rem;
        border-radius: 24px;
        text-align: center;
        color: white;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        margin-top: 1.5rem;
        animation: fadeIn 1s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .therapy-title {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .therapy-content {
        font-size: 2.5rem;
        font-weight: 800;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 4rem;
        color: rgba(255,255,255,0.7);
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <img src="https://cdn-icons-png.flaticon.com/512/3062/3062634.png" width="100">
        <h2 style="color: #333; margin-top: 1rem;">Adaptive AI</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("⚙️ Settings")
    use_camera = st.checkbox("Enable Facial Analysis", value=True, help="Uses your webcam to analyze facial expressions")
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info(
        "This advanced AI system combines Natural Language Processing (NLP) with Computer Vision to provide holistic mental health insights."
    )
    
    st.markdown("---")
    st.caption("© 2026 Adaptive AI Deployment")

# =====================================================
# MAIN CONTENT
# =====================================================

# Title Section
st.markdown("""
<div style="text-align: center; margin-bottom: 3rem;">
    <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem;">Mental Wellness Companion</h1>
    <p style="font-size: 1.2rem; opacity: 0.9;">Your safe space for emotional analysis and personalized therapy.</p>
</div>
""", unsafe_allow_html=True)

# Main Interaction Area
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.subheader("📝 How are you feeling?")
    text_input = st.text_area(
        "",
        placeholder="Share your thoughts here... (e.g., 'I realized today that I'm stronger than I thought.')",
        height=200,
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("✨ Analyze My State")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Placeholder or Results Area
    if not analyze_btn:
        st.markdown("""
        <div class="glass-container" style="text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;">
            <h3 style="color: white;">Waiting for input...</h3>
            <p>Enter your thoughts on the left and click Analyze.</p>
            <div style="font-size: 4rem; opacity: 0.5; margin-top: 1rem;">🧘</div>
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# ANALYSIS LOGIC
# =====================================================
if analyze_btn:
    if not text_input.strip():
        with col2:
            st.warning("⚠️ Please share your thoughts before we begin.")
    else:
        with col2:
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            with st.spinner("🔄 analyzing cognitive & emotional state..."):
                time.sleep(1.5) # UX delay for smooth transition
                
                try:
                    # Prepare payload
                    payload = {"text": text_input, "use_camera": use_camera}
                    
                    # Make API Request
                    response = requests.post(API_URL, json=payload, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        st.subheader("📊 Analysis Results")
                        
                        # Metrics Grid
                        c1, c2, c3 = st.columns(3)
                        
                        with c1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Text Emotion</div>
                                <div class="metric-value">{data.get('text_emotion', 'N/A')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        with c2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Facial Cues</div>
                                <div class="metric-value">{data.get('face_emotion', 'N/A')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        with c3:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Overall State</div>
                                <div class="metric-value" style="color: #667eea;">{data.get('final_emotion', 'N/A')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Therapy Recommendation
                        st.markdown(f"""
                        <div class="therapy-box">
                            <div class="therapy-title">Recommended Action</div>
                            <div class="therapy-content">{data.get('therapy', 'Consult a professional')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    else:
                        st.error(f"❌ Server Error: {response.status_code}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Connection Error: Backend server is not accessible.")
                    st.caption("Ensure `backend/app.py` is running.")
                except Exception as e:
                    st.error(f"⚠️ An unexpected error occurred: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# FOOTER
# =====================================================
st.markdown("""
<div class="footer">
    Made with ❤️ for Mental Health Awareness
</div>
""", unsafe_allow_html=True)
