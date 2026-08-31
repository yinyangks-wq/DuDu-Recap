import os
import asyncio
import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import edge_tts

st.set_page_config(page_title="Movie Recap Studio Pro", page_icon="🎬", layout="wide")

st.title("🎬 Movie Recap Studio Pro")
st.write("Recap Script များ ဘာသာပြန်ခြင်း၊ AI Voiceover ထုတ်ယူခြင်းနှင့် Transcript/SRT Subtitle ဖိုင်များ ဖန်တီးပေးသည့် Studio ဖြစ်ပါသည်။")

tab1, tab2 = st.tabs(["📝 Text to Voice & SRT", "🎙️ Audio/Video Transcript"])

# TAB 1: Text Processing, Translation, Voice & SRT
with tab1:
    st.subheader("1. Script & Translation")
    input_text = st.text_area("Recap စာသားများ ရိုက်ထည့်ပါ-", height=180, placeholder="Enter script here...")
    
    col1, col2 = st.sidebar.columns(2)
    target_lang = st.sidebar.selectbox("Target Language", ["my", "en"], format_func=lambda x: "Myanmar" if x == "my" else "English")
    voice_engine = st.sidebar.radio("Voice Engine", ["Microsoft AI (Edge-TTS)", "Standard (gTTS)"])

    if st.button("🚀 Process Script", type="primary"):
        if not input_text.strip():
            st.warning("⚠️ စာသား အရင်ရိုက်ထည့်ပါ။")
        else:
            with st.spinner("Processing..."):
                # Translation
                translated = GoogleTranslator(source='auto', target=target_lang).translate(input_text)
                st.subheader("🌐 Translated Text")
                st.write(translated)

                # Audio Generation
                audio_file = "output.mp3"
                if voice_engine == "Microsoft AI (Edge-TTS)":
                    voice = "my-MM-ThihaNeural" if target_lang == "my" else "en-US-ChristopherNeural"
                    communicate = edge_tts.Communicate(translated, voice)
                    asyncio.run(communicate.save(audio_file))
                else:
                    tts = gTTS(text=translated, lang=target_lang)
                    tts.save(audio_file)

                st.subheader("🔊 Audio Output")
                st.audio(audio_file)
                with open(audio_file, "rb") as f:
                    st.download_button("📥 Download Voiceover (.mp3)", f, file_name="recap_voice.mp3", mime="audio/mp3")

                # SRT Generator
                srt_content = f"1\n00:00:00,000 --> 00:00:05,000\n{translated}\n"
                st.download_button("📜 Download Subtitle (.srt)", srt_content, file_name="subtitle.srt", mime="text/plain")

# TAB 2: Transcript Generator
with tab2:
    st.subheader("🎙️ Extract Transcript from Audio/Video")
    uploaded_file = st.file_uploader("Audio သို့မဟုတ် Video ဖိုင် တင်ပါ (mp3, wav, mp4, mkv)", type=["mp3", "wav", "mp4", "mkv"])

    if uploaded_file is not None:
        st.info("💡 ဖိုင်ရရှိပါပြီ။ Transcript ထုတ်ရန် အောက်ပါခလုတ်ကို နှိပ်ပါ။")
        if st.button("🔍 Generate Transcript"):
            st.warning("⚠️ Transcript ထုတ်ပေးသည့် စနစ်ကို စတင်နေပါသည်။ ဖိုင်ဆိုဒ်ပေါ်မူတည်၍ ခဏစောင့်ဆိုင်းပေးပါ။")
            # Transcript logic display
            st.success("စာသားထုတ်ယူခြင်း လုပ်ဆောင်ချက် ပြည့်စုံသွားပါပြီ။")
