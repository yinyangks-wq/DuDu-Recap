import os
import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS

# Page Configuration
st.set_page_config(
    page_title="Movie Recap Studio",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Movie Recap Studio")
st.write("Movie recap စာမူများကို မြန်မာဘာသာသို့ ပြန်ဆိုပြီး အသံဖိုင် (Audio) ပြုလုပ်ပေးမည့် App ဖြစ်ပါတယ်၊၊")

# Sidebar - Language and Audio Settings
st.sidebar.header("⚙️ Settings")
target_lang = st.sidebar.selectbox(
    "Target Language",
    options=["my", "en"],
    format_func=lambda x: "Myanmar" if x == "my" else "English",
    index=0
)

# Text Input Area
st.subheader("📝 Input Script")
input_text = st.text_area(
    "Recap ရေးသားလိုသည့် စာသားများကို ဒီနေရာတွင် ရိုက်ထည့်ပါ သို့မဟုတ် Paste လုပ်ပါ-",
    height=200,
    placeholder="Enter script text here..."
)

if st.button("🚀 Process & Generate Audio", type="primary"):
    if not input_text.strip():
        st.warning("⚠️ စာသား အရင် ရိုက်ထည့်ပေးပါ။")
    else:
        with st.spinner("စာတိုကို ဘာသာပြန်ဆိုပြီး အသံဖိုင် ပြုလုပ်နေပါသည်..."):
            try:
                # Translation
                translated = GoogleTranslator(source='auto', target=target_lang).translate(input_text)
                
                st.subheader("🌐 Translated Script")
                st.write(translated)

                # Text-To-Speech (gTTS)
                tts = gTTS(text=translated, lang=target_lang, slow=False)
                audio_path = "output.mp3"
                tts.save(audio_path)

                # Audio Player & Download
                st.subheader("🔊 Generated Audio")
                st.audio(audio_path, format="audio/mp3")

                with open(audio_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Audio (.mp3)",
                        data=file,
                        file_name="recap_voice.mp3",
                        mime="audio/mp3"
                    )

            except Exception as e:
                st.error(f"❌ Error ဖြစ်သွားပါသည်: {e}")
