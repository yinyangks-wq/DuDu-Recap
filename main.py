import os
import asyncio
import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import edge_tts
from youtube_transcript_api import YouTubeTranscriptApi

st.set_page_config(page_title="Movie Recap Studio Pro", page_icon="🎬", layout="wide")

st.title("🎬 Movie Recap Studio Pro")
st.write("YouTube Video မှ Transcript ထုတ်ယူ ဘာသာပြန်ခြင်း၊ Text to Voiceover ပြုလုပ်ခြင်းနှင့် SRT Subtitle ဖန်တီးပေးသည့် Studio ဖြစ်ပါသည်။")

tab1, tab2 = st.tabs(["🔴 YouTube Transcript & Translator", "📝 Text to Voice & SRT"])

# FUNCTION: Extract YouTube Video ID
def get_youtube_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url

# TAB 1: YouTube Link to Transcript & Translation
with tab1:
    st.subheader("🔴 Extract & Translate YouTube Transcript")
    yt_url = st.text_input("YouTube Video Link ကို ထည့်ပါ-", placeholder="https://www.youtube.com/watch?ve=example")
    yt_lang = st.selectbox("Translate To", ["my", "en"], format_func=lambda x: "Myanmar" if x == "my" else "English")

    if st.button("🚀 Fetch & Translate Transcript", type="primary"):
        if not yt_url.strip():
            st.warning("⚠️ YouTube Link အရင်ထည့်ပါ။")
        else:
            with st.spinner("YouTube ထံမှ စာတန်းထိုးများကို ဆွဲထုတ်ပြီး ဘာသာပြန်ဆိုနေပါသည်..."):
                try:
                    video_id = get_youtube_id(yt_url)
                    
                    # Fetching transcript
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                    full_text = " ".join([item['text'] for item in transcript_list])
                    
                    st.success("✅ Transcript အောင်မြင်စွာ ရရှိပါပြီ။")
                    
                    col_left, col_right = st.columns(2)
                    
                    with col_left:
                        st.subheader("📄 Original Transcript")
                        st.text_area("မူရင်း စာသားများ:", full_text, height=250)
                    
                    # Translation
                    translated_text = GoogleTranslator(source='auto', target=yt_lang).translate(full_text)
                    
                    with col_right:
                        st.subheader("🌐 Translated Transcript")
                        st.text_area("ဘာသာပြန် စာသားများ:", translated_text, height=250)

                    # SRT Generator Logic
                    srt_content = ""
                    for idx, item in enumerate(transcript_list, 1):
                        start = item['start']
                        duration = item['duration']
                        end = start + duration
                        
                        start_str = f"{int(start//3600):02d}:{int((start%3600)//60):02d}:{int(start%60):02d},000"
                        end_str = f"{int(end//3600):02d}:{int((end%3600)//60):02d}:{int(end%60):02d},000"
                        
                        srt_content += f"{idx}\n{start_str} --> {end_str}\n{item['text']}\n\n"

                    st.download_button("📜 Download Translated SRT Subtitle", srt_content, file_name="youtube_subtitle.srt", mime="text/plain")

                except Exception as e:
                    st.error(f"❌ Transcript ဆွဲထုတ်၍ မရပါ (ဗီဒီယိုတွင် Subtitle မပါဝင်ပါ သို့မဟုတ် Link မှားယွင်းနေပါသည်): {e}")

# TAB 2: Text Processing, Voice & SRT
with tab2:
    st.subheader("📝 Script to Voiceover")
    input_text = st.text_area("Recap စာသားများ ရိုက်ထည့်ပါ-", height=180, placeholder="Enter script here...")
    
    col1, col2 = st.sidebar.columns(2)
    target_lang = st.sidebar.selectbox("Target Language", ["my", "en"], format_func=lambda x: "Myanmar" if x == "my" else "English", key="tab2_lang")
    voice_engine = st.sidebar.radio("Voice Engine", ["Microsoft AI (Edge-TTS)", "Standard (gTTS)"])

    if st.button("🚀 Process Script"):
        if not input_text.strip():
            st.warning("⚠️ စာသား အရင်ရိုက်ထည့်ပါ။")
        else:
            with st.spinner("Processing..."):
                translated = GoogleTranslator(source='auto', target=target_lang).translate(input_text)
                st.subheader("🌐 Translated Text")
                st.write(translated)

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
