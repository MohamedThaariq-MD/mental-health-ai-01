import streamlit as st
import requests
import time

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Adaptive Cognitive Mental Health AI",
    page_icon="🧠",
    layout="wide"
)

# -------------------------------
# CUSTOM CSS (BRIGHT + ELEGANT)
# -------------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
}
.main {
    background-color: #ffffff;
    border-radius: 16px;
    padding: 2rem;
}
h1 {
    color: #4b6cb7;
}
h2, h3 {
    color: #182848;
}
.emotion-box {
    background: #f0f4ff;
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.therapy-box {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    font-size: 1.2rem;
}
.footer {
    text-align: center;
    color: #666;
    font-size: 0.85rem;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.markdown("<h1>🧠 Adaptive Cognitive Mental Health AI</h1>", unsafe_allow_html=True)
st.markdown(
    "### Emotion-Aware Therapy Recommendation System  \n"
    "**Bright • Intelligent • Personalized • Real-Time**"
)

st.divider()

# -------------------------------
# LAYOUT
# -------------------------------
left_col, right_col = st.columns([1.2, 1])

# -------------------------------
# LEFT COLUMN – USER INPUT
# -------------------------------
with left_col:
    st.subheader("💬 Express Yourself")
    text = st.text_area(
        "How are you feeling today?",
        placeholder="Example: I feel stressed, lonely, and mentally exhausted...",
        height=160
    )

    analyze_btn = st.button("✨ Analyze My Emotion", use_container_width=True)

# -------------------------------
# RIGHT COLUMN – INFO PANEL
# -------------------------------
with right_col:
    st.subheader("📌 System Highlights")
    st.info(
        "• Transformer-based NLP (Text Emotion)\n"
        "• Facial Emotion Analysis\n"
        "• Reinforcement Learning Therapy Engine\n"
        "• Real-time Adaptive Feedback\n"
        "• SDG-3 Aligned Mental Health AI"
    )

# -------------------------------
# ANALYSIS LOGIC
# -------------------------------
if analyze_btn:
    if text.strip() == "":
        st.warning("⚠️ Please enter how you feel before analysis.")
    else:
        with st.spinner("🔍 Understanding your emotions..."):
            time.sleep(1.2)

            try:
                response = requests.post(
                    "http://127.0.0.1:5000/analyze",
                    json={"text": text},
                    timeout=10
                )

                data = response.json()

                st.divider()
                st.subheader("📊 Emotion Analysis Results")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(
                        f"<div class='emotion-box'><b>Text Emotion</b><br>{data.get('text_emotion')}</div>",
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown(
                        f"<div class='emotion-box'><b>Face Emotion</b><br>{data.get('face_emotion')}</div>",
                        unsafe_allow_html=True
                    )

                with col3:
                    st.markdown(
                        f"<div class='emotion-box'><b>Final Emotion</b><br>{data.get('final_emotion')}</div>",
                        unsafe_allow_html=True
                    )

                st.divider()
                st.subheader("🧘 Personalized Therapy Recommendation")

                st.markdown(
                    f"<div class='therapy-box'>{data.get('therapy')}</div>",
                    unsafe_allow_html=True
                )

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to local backend.")
                st.info("Make sure backend is running on http://127.0.0.1:5000")

            except requests.exceptions.Timeout:
                st.error("❌ Backend request timed out.")

            except Exception as e:
                st.error("Unexpected error occurred:")
                st.error(e)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("""
<div class="footer">
Adaptive Cognitive AI Framework for Personalized Mental Health Monitoring  
<br>Phase-2 & Phase-3 | Local Deployment
</div>
""", unsafe_allow_html=True)
