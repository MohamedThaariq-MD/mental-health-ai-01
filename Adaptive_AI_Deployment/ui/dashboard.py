import sys
import os
import time
import streamlit as st
import requests

# =====================================================
# PROJECT PATH FIX
# =====================================================
import uuid
import json

# =====================================================
# PROJECT PATH FIX
# =====================================================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# CONFIGURATION
# =====================================================
API_URL = "http://127.0.0.1:5000/analyze"
API_BASE_URL = "http://127.0.0.1:5000"
SESSION_FILE = "user_session.json"

def get_persistent_session_id():
    """Load or create a persistent session ID."""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                return data.get("session_id", str(uuid.uuid4()))
        except:
            pass
            
    new_id = str(uuid.uuid4())
    with open(SESSION_FILE, "w") as f:
        json.dump({"session_id": new_id}, f)
    return new_id

# Initialize Session
if "user_session_id" not in st.session_state:
    st.session_state.user_session_id = get_persistent_session_id()


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

    /* Background with dark, pleasant animated gradient */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e293b, #334155, #1e1b4b);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Glassmorphism Containers - Darker */
    .glass-container {
        background: rgba(30, 41, 59, 0.4);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 2rem;
        margin-bottom: 2rem;
    }

    /* Section Headers */
    h1, h2, h3 {
        color: #f8fafc;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    p, label {
        color: #94a3b8;
        font-weight: 400;
    }

    /* Input Area */
    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        font-size: 1rem;
        color: #f8fafc;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
    }
    .stTextArea textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 30px rgba(99, 102, 241, 0.4);
        border-color: transparent;
    }

    /* Result Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: transform 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        background: rgba(30, 41, 59, 0.9);
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 0.5rem;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.4rem;
        font-weight: 800;
    }

    /* Therapy Recommendation */
    .therapy-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2.5rem;
        border-radius: 24px;
        text-align: center;
        color: #f8fafc;
        border: 1px solid rgba(99, 102, 241, 0.2);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
        margin-top: 1.5rem;
        animation: fadeIn 1s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .therapy-title {
        font-size: 1.1rem;
        color: #6366f1;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 700;
    }
    .therapy-content {
        font-size: 2.5rem;
        font-weight: 800;
        color: #f8fafc;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 4rem;
        color: #475569;
        font-size: 0.9rem;
    }

    /* WhatsApp Style Chat Bubbles */
    .chat-row {
        display: flex;
        width: 100%;
        margin-bottom: 1rem;
    }
    .user-row {
        justify-content: flex-end;
    }
    .ai-row {
        justify-content: flex-start;
    }
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 15px;
        max-width: 70%;
        color: #e2e8f0;
        font-size: 1rem;
        line-height: 1.5;
        box-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    .user-bubble {
        background-color: #005c4b; /* WhatsApp Dark Green */
        border-top-right-radius: 0;
        text-align: left; /* Text inside is typically left aligned even if bubble is right */
    }
    .ai-bubble {
        background-color: #202c33; /* WhatsApp Dark Grey */
        border-top-left-radius: 0;
    }
    
</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <img src="https://cdn-icons-png.flaticon.com/512/3062/3062634.png" width="80" style="filter: hue-rotate(240deg) brightness(1.2);">
        <h2 style="color: #f8fafc; margin-top: 1rem;">Wellness AI</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Interaction Mode Switcher
    st.subheader("🎭 Interaction Mode")
    interaction_mode = st.radio(
        "Choose your experience:",
        ["Wholesome Conversation", "Therapy Recommendations"],
        index=0,
        help="Switch between chat-focused or recommendation-focused views."
    )
    
    st.markdown("---")

    st.header("⚙️ Settings")
    
    # Camera only available in Therapy Mode
    if interaction_mode == "Therapy Recommendations":
        use_camera = st.checkbox("Enable Facial Analysis", value=True, help="Uses your webcam to analyze facial expressions")
    else:
        use_camera = False

    # Audio Input (Moved to Sidebar for Clean Chat UI)
    audio_value = None
    if interaction_mode == "Wholesome Conversation":
        st.subheader("🎤 Voice Input")
        audio_value = st.audio_input("Record Voice Message", key="sidebar_mic")

    st.markdown("---")
    
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.latest_analysis = {}
        st.rerun()

    st.markdown("---")
    st.caption("© 2026 Adaptive AI Deployment")

    # Sidebar Wellness Panel (Always shows latest results)
    if "latest_analysis" in st.session_state and st.session_state.latest_analysis:
        st.markdown("---")
        st.markdown("### 🧘 Latest Wellness Insights")
        data = st.session_state.latest_analysis
        
        st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.1); padding: 1rem; border-radius: 10px; border: 1px solid rgba(99, 102, 241, 0.2);">
            <p style="margin-bottom: 0.2rem; font-size: 0.8rem; color: #818cf8; text-transform: uppercase; font-weight: 700;">Overall State</p>
            <h4 style="margin: 0; color: #f8fafc;">{data.get('final_emotion', 'N/A')}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**Suggestion:** {data.get('therapy')}")
        
        with st.expander("More details"):
            st.write(f"**Text:** {data.get('text_emotion')}")
            st.write(f"**Face:** {data.get('face_emotion')}")
            if data.get('face_feature_desc'):
                st.info(data.get('face_feature_desc'))

# =====================================================
# MAIN CONTENT
# =====================================================

# =====================================================
# RENDER FUNCTIONS
# =====================================================

def render_chat_interface():
    """Renders the WhatsApp-style split chat UI"""
    
    st.markdown('<div style="margin-bottom: 60px;">', unsafe_allow_html=True) # Spacer
    
    # Display Chat History with Custom Bubbles
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.markdown(f"""
            <div class="chat-row user-row">
                <div class="chat-bubble user-bubble">
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-row ai-row">
                <div class="chat-bubble ai-bubble">
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Use Native Streamlit Chat Input (Fixed at bottom)
    # This renders automatically at the bottom, no need for manual placement
    user_input = st.chat_input("Tell me what's on your mind...")
    
    return user_input

def render_therapy_interface():
    """Renders the new Therapy Session Dashboard UI"""
    
    st.markdown("## 🛋️ Therapy Session Check-In")
    
    # Top Section: Input
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.4); border-radius: 16px; padding: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 2rem;">
        <h4 style="margin-top:0; color: #94a3b8; font-weight: 500;">How are you feeling right now?</h4>
    </div>
    """, unsafe_allow_html=True)

    # Input Row (Text Only) - Reusing the accessible layout
    col1, col2 = st.columns([6, 1])
    with col1:
        def submit_therapy_text():
            st.session_state.prompt_input = st.session_state.therapy_input
            st.session_state.therapy_input = ""
            
        st.text_input(
            "Share your thoughts...", 
            key="therapy_input", 
            on_change=submit_therapy_text,
            label_visibility="collapsed",
            placeholder="I'm feeling..."
        )
    with col2:
        if st.button("Analyze", use_container_width=True):
            submit_therapy_text()

    if use_camera:
        st.caption("📷 Facial Analysis Active")

    # Results Section - Only verify if we have a LATEST analysis that matches the current session interaction
    # For now, we just show the latest analysis if it exists
    if st.session_state.latest_analysis:
        data = st.session_state.latest_analysis
        
        # Face Tracking Dashboard (New Feature)
        if data.get("processed_frame"):
            with st.expander("👁️ Face Tracking Dashboard (Golden Ratio Analysis)", expanded=True):
                col_video, col_info = st.columns([2, 1])
                with col_video:
                    # Decode base64 image
                    import base64
                    try:
                        img_bytes = base64.b64decode(data["processed_frame"])
                        st.image(img_bytes, caption="Live Facial Analysis & Golden Ratio", use_container_width=True)
                    except Exception as e:
                        st.error(f"Could not display face tracking: {e}")
                
                with col_info:
                    st.markdown("### Analysis Details")
                    st.markdown(f"**Emotion:** {data.get('final_emotion', 'N/A')}")
                    st.markdown(f"**Description:** {data.get('face_feature_desc', 'No details')}")
                    st.caption("The golden lines represent aesthetic geometric ratios used for facial symmetry analysis.")

        st.markdown("---")
        st.subheader("💡 Analysis & Insights")
        
        # 0. Final Declaration (Hero Section)
        final_decl = data.get('final_declaration', f"You seem {data.get('text_emotion', 'neutral')} and your face looks {data.get('face_emotion', 'neutral')}.")
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%); 
                    border-left: 5px solid #818cf8; border-radius: 8px; padding: 1.5rem; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="margin: 0; color: #e2e8f0; font-weight: 300; font-style: italic;">"{final_decl}"</h3>
        </div>
        """, unsafe_allow_html=True)

        # 1. Detailed Analytics (Split View)
        col_text, col_face = st.columns(2)
        
        with col_text:
            text_emo = data.get('text_emotion', 'Neutral')
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label" style="color: #94a3b8;">📝 Text Analysis</div>
                <div class="metric-value" style="color: #fca5a5;">{text_emo}</div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.5rem;">Based on your words</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_face:
            face_emo = data.get('face_emotion', 'Neutral')
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label" style="color: #94a3b8;">😶 Face Analysis</div>
                <div class="metric-value" style="color: #93c5fd;">{face_emo}</div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.5rem;">Based on expressions</div>
            </div>
            """, unsafe_allow_html=True)

        # 1.5 AI Therapist Notes (Restored)
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.6); border-radius: 16px; padding: 1.5rem; margin-top: 1.5rem; border: 1px solid rgba(167, 139, 250, 0.2);">
            <div style="color: #a78bfa; font-weight: 600; margin-bottom: 0.5rem;">💬 AI Therapist Notes</div>
            <div style="color: #e2e8f0; font-size: 1.05rem; line-height: 1.6;">
                {data.get('conversational_response', 'Analysis complete. See recommendations below.')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. Recommendations Grid
        st.markdown("### 🌟 Recommended For You")
        
        # Helper for Feedback
        def send_feedback(emotion, action, reward, category_name):
            try:
                payload = {
                    "session_id": st.session_state.user_session_id,
                    "emotion": data.get("final_emotion"),
                    "action": action,
                    "reward": reward
                }
                requests.post(f"{API_BASE_URL}/feedback", json=payload)
                st.toast(f"Thanks! I'll improve my {category_name} suggestions. 🧠")
            except:
                st.error("Could not send feedback.")

        # Row 1: Activity & Therapy
        r1_col1, r1_col2 = st.columns(2)
        with r1_col1:
            st.markdown(f"""
            <div class="metric-card" style="align-items: flex-start; text-align: left; background: rgba(30, 41, 59, 0.4);">
                <div class="metric-label" style="color: #34d399;">🏃 Activity</div>
                <div style="color: #f1f5f9; font-weight: 500;">{data.get('activity', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
        with r1_col2:
            st.markdown(f"""
            <div class="metric-card" style="align-items: flex-start; text-align: left; background: rgba(30, 41, 59, 0.4);">
                <div class="metric-label" style="color: #f472b6;">🧘 Therapy Strategy</div>
                <div style="color: #f1f5f9; font-weight: 500;">{data.get('therapy', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Row 2: Entertainment (Music, Movie, Game) with FEEDBACK
        r2_col1, r2_col2, r2_col3 = st.columns(3)
        
        # Music
        with r2_col1:
            music_item = data.get('music', 'N/A')
            st.markdown(f"""
            <div class="metric-card" style="align-items: flex-start; text-align: left; background: rgba(30, 41, 59, 0.4); margin-bottom: 0.5rem;">
                <div class="metric-label" style="color: #fbbf24;">🎵 Song</div>
                <div style="color: #f1f5f9; font-size: 0.95rem; min-height: 3rem;">{music_item}</div>
            </div>
            """, unsafe_allow_html=True)
            fb_c1, fb_c2 = st.columns(2)
            if fb_c1.button("👍", key=f"like_music", use_container_width=True):
                send_feedback(data.get("final_emotion"), music_item, 1, "music")
            if fb_c2.button("👎", key=f"dislike_music", use_container_width=True):
                 send_feedback(data.get("final_emotion"), music_item, -1, "music")

        # Movie
        with r2_col2:
            movie_item = data.get('movie', 'N/A')
            st.markdown(f"""
            <div class="metric-card" style="align-items: flex-start; text-align: left; background: rgba(30, 41, 59, 0.4); margin-bottom: 0.5rem;">
                <div class="metric-label" style="color: #a78bfa;">🎬 Movie</div>
                <div style="color: #f1f5f9; font-size: 0.95rem; min-height: 3rem;">{movie_item}</div>
            </div>
            """, unsafe_allow_html=True)
            fb_c1, fb_c2 = st.columns(2)
            if fb_c1.button("👍", key=f"like_movie", use_container_width=True):
                send_feedback(data.get("final_emotion"), movie_item, 1, "movie")
            if fb_c2.button("👎", key=f"dislike_movie", use_container_width=True):
                 send_feedback(data.get("final_emotion"), movie_item, -1, "movie")

        # Game
        with r2_col3:
            game_item = data.get('game', 'N/A')
            st.markdown(f"""
            <div class="metric-card" style="align-items: flex-start; text-align: left; background: rgba(30, 41, 59, 0.4); margin-bottom: 0.5rem;">
                <div class="metric-label" style="color: #2dd4bf;">🎮 Game</div>
                <div style="color: #f1f5f9; font-size: 0.95rem; min-height: 3rem;">{game_item}</div>
            </div>
            """, unsafe_allow_html=True)
            fb_c1, fb_c2 = st.columns(2)
            if fb_c1.button("👍", key=f"like_game", use_container_width=True):
                send_feedback(data.get("final_emotion"), game_item, 1, "game")
            if fb_c2.button("👎", key=f"dislike_game", use_container_width=True):
                 send_feedback(data.get("final_emotion"), game_item, -1, "game")

    return None

# =====================================================
# MAIN CONTENT CONTROLLER
# =====================================================

# Title Section
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 style="font-size: 3rem; margin-bottom: 0.5rem; background: linear-gradient(to right, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Your Mental Wellness Friend</h1>
    <p style="font-size: 1.1rem; color: #94a3b8;">I'm here to listen, support, and help you feel better. Let's talk! 💙</p>
</div>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "latest_analysis" not in st.session_state:
    st.session_state.latest_analysis = {}

# Render Interface based on Mode
chat_input_value = None
if interaction_mode == "Wholesome Conversation":
    chat_input_value = render_chat_interface()
else:
    render_therapy_interface()


# =====================================================
# DATA PROCESSING (COMMON)
# =====================================================

# Prompt Handling Logic
prompt = None

# 1. Text Input via st.chat_input (High Priority)
if chat_input_value:
    prompt = chat_input_value

# 2. explicit text submission via other box (Therapy Mode)
elif "prompt_input" in st.session_state and st.session_state.prompt_input:
    prompt = st.session_state.prompt_input
    st.session_state.prompt_input = None

# 3. Audio Input via Sidebar (Medium Priority)
# Only process if we haven't processed this exact audio value before
elif audio_value and audio_value != st.session_state.get("last_audio_value"):
    # Stale audio prevention
    st.session_state.last_audio_value = audio_value
    
    with st.spinner("Transcribing..."):
        try:
            files = {"file": ("audio.wav", audio_value, "audio/wav")}
            transcribe_res = requests.post(f"{API_BASE_URL}/transcribe", files=files)
            
            if transcribe_res.status_code == 200:
                prompt = transcribe_res.json().get("text")
            else:
                st.error("Could not transcribe audio.")
        except Exception as e:
            st.error(f"Error during transcription: {e}")

# Process Input if prompt exists
if prompt:
    # Add user message to history (for chat mode mostly, but good to keep record)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Process with Backend
    with st.spinner("🔄 Analying your state..."):
        try:
            # Prepare payload
            payload = {
                "text": prompt, 
                "use_camera": use_camera,
                "session_id": st.session_state.user_session_id
            }
            
            # Make API Request
            response = requests.post(API_URL, json=payload, timeout=45)
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.latest_analysis = data
                
                # Get the conversational response (new empathetic format)
                conversational_response = data.get("conversational_response")
                
                if conversational_response:
                    
                    # TTS Playback
                    try:
                        tts_response = requests.post(f"{API_BASE_URL}/tts", json={"text": conversational_response})
                        if tts_response.status_code == 200:
                            st.audio(tts_response.content, format="audio/mp3", autoplay=True)
                    except Exception as e:
                        print(f"TTS Error: {e}")

                    # Add to history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": conversational_response,
                        "analysis": data
                    })
                    
                else:
                    # Fallback
                    ai_response = f"I've analyzed your emotional state and detected a **{data.get('final_emotion', 'neutral')}** tone."
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": ai_response,
                        "analysis": data
                    })
                
                # Rerun to update UI
                st.rerun()
                
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", "Unknown error")
                    st.error(f"❌ Server Error: {response.status_code} - {error_msg}")
                except:
                    st.error(f"❌ Server Error: {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection Error: Backend server is not accessible.")
        except Exception as e:
            st.error(f"⚠️ An unexpected error occurred: {str(e)}")


# =====================================================
# FOOTER
# =====================================================
st.markdown("""
<div class="footer">
    Developed for Adaptive AI Emotional Intelligence System • 2026
</div>
""", unsafe_allow_html=True)
