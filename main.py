import os
import asyncio
import streamlit as st
from deep_translator import GoogleTranslator
import edge_tts
from youtube_transcript_api import YouTubeTranscriptApi

# 1. Page Config & CSS Styling
st.set_page_config(
    page_title="Movie Recap Studio Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI Enhancement
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #A0AAB0;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Header Design
st.markdown('<div class="main-header">🎬 Movie Recap Studio Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Professional Video Recap Automation Tool</div>', unsafe_allow_html=True)
st.divider()

# 3. Sidebar Navigation Menu
st.sidebar.image("https://img.icons8.com/color/96/movie-beginning.png", width=70)
st.sidebar.title("Studio Menu")
app_mode = st.sidebar.radio(
    "အသုံးပြုလိုသည့် စနစ်ကို ရွေးပါ-",
    [
        "📝 Text to Voiceover",
        "🔴 YouTube Subtitle & SRT",
        "🎙️ Audio/Video Translator"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("⚙️ **Audio Settings**")
voice_speed = st.sidebar.slider("Voice Speed (%)", min_value=-50, max_value=50, value=0, step=5)
speed_str = f"{'+' if voice_speed >= 0 else ''}{voice_speed}%"

# Utility: SRT Time Formatter
def format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

# ---------------------------------------------------------
# PAGE 1: TEXT TO VOICEOVER
# ---------------------------------------------------------
if app_mode == "📝 Text to Voiceover":
    st.subheader("📝 Script to Myanmar Voiceover")
    
    col_in, col_out = st.columns([1, 1], gap="large")
    
    with col_in:
        input_text = st.text_area("Recap စာသားများ ရိုက်ထည့်ပါ-", height=250, placeholder="Enter script here...")
        process_btn = st.button("🚀 Process & Generate Audio", type="primary")

    with col_out:
        if process_btn:
            if not input_text.strip():
                st.warning("⚠️ စာသား အရင် ရိုက်ထည့်ပေးပါ။")
            else:
                with st.spinner("စာတိုကို ဘာသာပြန်ဆိုပြီး အသံဖိုင် ပြုလုပ်နေပါသည်..."):
                    try:
                        translated = GoogleTranslator(source='auto', target='my').translate(input_text)
                        
                        st.markdown("**🌐 Myanmar Script:**")
                        st.info(translated)

                        audio_file = "recap_voice.mp3"
                        communicate = edge_tts.Communicate(translated, "my-MM-ThihaNeural", rate=speed_str)
                        asyncio.run(communicate.save(audio_file))

                        st.markdown("**🔊 Generated Voiceover:**")
                        st.audio(audio_file)
                        
                        with open(audio_file, "rb") as f:
                            st.download_button("📥 Download Audio (.mp3)", f, file_name="recap_voice.mp3", mime="audio/mp3", use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

# ---------------------------------------------------------
# PAGE 2: YOUTUBE SUBTITLE & SRT
# ---------------------------------------------------------
elif app_mode == "🔴 YouTube Subtitle & SRT":
    st.subheader("🔴 Extract & Translate YouTube Transcript")
    
    yt_url = st.text_input("YouTube Video Link ကို ထည့်ပါ-", placeholder="https://www.youtube.com/watch?v=example")
    
    if st.button("🚀 Extract & Translate Subtitle", type="primary"):
        if not yt_url.strip():
            st.warning("⚠️ YouTube Link ထည့်ပေးပါ။")
        else:
            with st.spinner("Transcript ဆွဲထုတ်ပြီး မြန်မာလို ဘာသာပြန်နေပါသည်..."):
                try:
                    if "v=" in yt_url:
                        video_id = yt_url.split("v=")[1].split("&")[0]
                    elif "youtu.be/" in yt_url:
                        video_id = yt_url.split("youtu.be/")[1].split("?")[0]
                    else:
                        video_id = yt_url

                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                    
                    srt_content = ""
                    translated_lines = []
                    translator = GoogleTranslator(source='auto', target='my')

                    for idx, item in enumerate(transcript_list, 1):
                        start_time = format_srt_time(item['start'])
                        end_time = format_srt_time(item['start'] + item['duration'])
                        my_text = translator.translate(item['text'])
                        translated_lines.append(my_text)
                        srt_content += f"{idx}\n{start_time} --> {end_time}\n{my_text}\n\n"

                    st.success("✅ Extracting & Translating Completed!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**📄 Myanmar Script Output:**")
                        st.text_area("Full Text:", " ".join(translated_lines), height=250)
                    with col2:
                        st.markdown("**📜 CapCut/VN Ready Subtitle (.srt):**")
                        st.download_button("📥 Download Synced SRT File", srt_content, file_name="synced_myanmar_subtitle.srt", mime="text/plain", use_container_width=True)

                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ---------------------------------------------------------
# PAGE 3: AUDIO/VIDEO TRANSLATOR
# ---------------------------------------------------------
elif app_mode == "🎙️ Audio/Video Translator":
    st.subheader("🎙️ Import Audio/Video ➔ Myanmar Voiceover")
    
    uploaded_file = st.file_uploader("Audio/Video ဖိုင် တင်ပါ (mp3, wav, mp4, mkv)", type=["mp3", "wav", "mp4", "mkv"])
    
    if uploaded_file is not None:
        st.audio(uploaded_file)
        st.info("💡 ဖိုင် ထည့်သွင်းပြီးပါပြီ။ Whisper Model ကို Streamlit Cloud ပေါ်တွင် လိုအပ်ပါက အဆင့်မြှင့်တင် အသုံးပြုနိုင်ပါသည်။")
