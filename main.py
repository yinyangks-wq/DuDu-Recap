import streamlit as st
import asyncio
import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io

st.set_page_config(page_title="Movie Recap All-in-One Tool", page_icon="🎬", layout="centered")

st.title("🎬 Movie Recap Auto Generator")
st.write("Voiceover (.mp3)၊ Subtitle (.srt) နှင့် Thumbnail Image များကို တစ်နေရာတည်းတွင် ဖန်တီးပါ")

tab1, tab2 = st.tabs(["🎙️ Voice & Subtitle", "🖼️ Thumbnail Generator"])

# ----------------- TAB 1: VOICE & SRT -----------------
with tab1:
    script_text = st.text_area("Recap Script စာသားများကို ဒီမှာ Paste လုပ်ပါ:", height=200)

    voice_option = st.selectbox(
        "အသံအမျိုးအစား ရွေးပါ:",
        [
            ("မြန်မာ - Nilar (Female)", "my-MM-NilarNeural"),
            ("မြန်မာ - Thiha (Male)", "my-MM-ThihaNeural"),
            ("English - Christopher (Male)", "en-US-ChristopherNeural"),
            ("English - Ava (Female)", "en-US-AvaNeural")
        ],
        format_func=lambda x: x[0]
    )

    def text_to_srt(text):
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        srt_content = ""
        start_time = 0
        for i, line in enumerate(lines, 1):
            duration = max(2, len(line) * 0.25)
            end_time = start_time + duration
            
            def format_time(seconds):
                hrs = int(seconds // 3600)
                mins = int((seconds % 3600) // 60)
                secs = int(seconds % 60)
                msecs = int((seconds - int(seconds)) * 1000)
                return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"
            
            srt_content += f"{i}\n{format_time(start_time)} --> {format_time(end_time)}\n{line}\n\n"
            start_time = end_time
        return srt_content

    async def generate_audio_file(text, voice_code):
        communicate = edge_tts.Communicate(text, voice_code)
        await communicate.save("output_voice.mp3")

    if st.button("🚀 Audio နှင့် SRT ထုတ်ယူမည်"):
        if script_text.strip():
            with st.spinner("Audio နှင့် Subtitle ဖန်တီးနေပါသည်..."):
                asyncio.run(generate_audio_file(script_text, voice_option[1]))
                srt_data = text_to_srt(script_text)
                
                st.success("✨ အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ!")
                
                audio_file = open("output_voice.mp3", "rb")
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/mp3")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button("📥 Download Audio (.mp3)", data=audio_bytes, file_name="recap_voice.mp3", mime="audio/mp3")
                with col2:
                    st.download_button("📥 Download Subtitle (.srt)", data=srt_data, file_name="recap_subtitles.srt", mime="text/plain")
        else:
            st.error("Script စာသား ထည့်ပေးပါ၊")

# ----------------- TAB 2: THUMBNAIL GENERATOR -----------------
with tab2:
    st.subheader("🖼️ High-Catchy Thumbnail Generator")
    
    bg_file = st.file_upload_button if hasattr(st, "file_upload_button") else st.file_uploader("နောက်ခံ Movie Scene ပုံ တင်ပါ (Optional):", type=["jpg", "png", "jpeg"])
    
    title_text = st.text_input("ခေါင်းစဉ် စာသား (Hook Title):", "ဒီဇာတ်လမ်းက တကယ်ရူးသွပ်စရာပဲ!")
    badge_text = st.text_input("အပေါ် တန်းစာသား (Badge Text):", "MOVIE RECAP")
    
    format_type = st.radio("Format ရွေးပါ:", ["TikTok / Reels (9:16)", "YouTube (16:9)"], horizontal=True)

    if st.button("🎨 Thumbnail ဖန်တီးမည်"):
        # Dimensions
        if "9:16" in format_type:
            width, height = 1080, 1920
        else:
            width, height = 1280, 720
            
        # Background Processing
        if bg_file is not None:
            bg_img = Image.open(bg_file).convert("RGBA")
            bg_img = bg_img.resize((width, height))
        else:
            bg_img = Image.new("RGBA", (width, height), (20, 20, 30, 255))
            
        # Dark Overlay for Text Readability
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 100))
        img = Image.alpha_composite(bg_img, overlay)
        draw = ImageDraw.Draw(img)
        
        # Draw Decorative Banner Box
        box_top = int(height * 0.65)
        box_bottom = int(height * 0.82)
        draw.rectangle([(50, box_top), (width - 50, box_bottom)], fill=(255, 0, 50, 210))
        
        # Note: Default font used for general compatibility
        font = ImageFont.load_default()
        
        # Draw Title Text
        draw.text((70, box_top + 40), title_text, fill=(255, 255, 255), font=font)
        draw.text((70, 40), f"[{badge_text}]", fill=(255, 220, 0), font=font)
        
        # Save image to memory buffer
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=95)
        byte_im = buf.getvalue()
        
        st.image(byte_im, caption="Generated Thumbnail Preview", use_container_width=True)
        st.download_button("📥 Download Thumbnail (.jpg)", data=byte_im, file_name="thumbnail.jpg", mime="image/jpeg")
