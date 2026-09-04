import streamlit as st
import asyncio
import edge_tts
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Movie Recap All-in-One Tool", page_icon="🎬", layout="centered")

st.title("🎬 Movie Recap Auto Generator")
st.write("Voiceover (.mp3)၊ Subtitle (.srt) နှင့် Thumbnail Variations များစွာကို ဖန်တီးပါ")

tab1, tab2 = st.tabs(["🎙️ Voice & Subtitle", "🖼️ Multi-Thumbnail Generator"])

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
            st.error("Script စာသား ထည့်ပေးပါ။")

# ----------------- TAB 2: MULTI-VARIATION THUMBNAIL GENERATOR -----------------
with tab2:
    st.subheader("🖼️ Multi-Variation Thumbnail Generator")
    st.write("ပုံများ တင်လိုက်ပါက ဒီဇိုင်းပုံစံ မတူညီသော Thumbnail ၄ မျိုးကို တစ်ပြိုင်နက် ထုတ်ပေးမည်ဖြစ်သည်")
    
    uploaded_files = st.file_uploader(
        "Movie Scene ပုံများ (၂ ပုံမှ ၄ ပုံအထိ ရွေးပေးပါ):", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True
    )
    
    title_text = st.text_input("ခေါင်းစဉ် စာသား (Hook Title):", "ဒီဇာတ်လမ်းက တကယ်ရူးသွပ်စရာပဲ!")
    badge_text = st.text_input("အပေါ်တန်း စာသား (Badge Text):", "MOVIE RECAP")
    format_type = st.radio("Format ရွေးပါ:", ["TikTok / Reels (9:16)", "YouTube (16:9)"], horizontal=True)

    def crop_fit(img, target_w, target_h):
        w, h = img.size
        target_ratio = target_w / target_h
        img_ratio = w / h
        if img_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img_cropped = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            img_cropped = img.crop((0, top, w, top + new_h))
        return img_cropped.resize((target_w, target_h))

    # Layout 1: Classic Split
    def generate_style_1(images, title, badge, width, height, is_vert):
        canvas = Image.new("RGBA", (width, height), (15, 15, 20, 255))
        num = len(images)
        if is_vert:
            sh = height // num
            for idx, img in enumerate(images):
                canvas.paste(crop_fit(img, width, sh), (0, idx * sh))
        else:
            sw = width // num
            for idx, img in enumerate(images):
                canvas.paste(crop_fit(img, sw, height), (idx * sw, 0))
                
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        d_overlay = ImageDraw.Draw(overlay)
        for y in range(int(height * 0.5), height):
            alpha = int(220 * ((y - height * 0.5) / (height * 0.5)))
            d_overlay.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
            
        canvas = Image.alpha_composite(canvas, overlay)
        draw = ImageDraw.Draw(canvas)
        b_top = int(height * 0.72)
        draw.rectangle([(40, b_top), (width - 40, b_top + 220)], fill=(230, 25, 50, 220))
        font = ImageFont.load_default()
        draw.text((60, b_top + 40), title, fill=(255, 255, 255), font=font)
        draw.text((60, 40), f"[{badge}]", fill=(255, 215, 0), font=font)
        return canvas

    # Layout 2: Hero Main + Sub-Cards
    def generate_style_2(images, title, badge, width, height, is_vert):
        canvas = Image.new("RGBA", (width, height), (15, 15, 20, 255))
        # Hero Image (Main)
        hero = crop_fit(images[0], width, height)
        canvas.paste(hero, (0, 0))
        
        # Bottom Overlay
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        d_overlay = ImageDraw.Draw(overlay)
        for y in range(int(height * 0.35), height):
            alpha = int(230 * ((y - height * 0.35) / (height * 0.65)))
            d_overlay.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
        canvas = Image.alpha_composite(canvas, overlay)
        
        # Sub Images Cards
        if len(images) > 1:
            sub_imgs = images[1:]
            c_w = (width - 100) // len(sub_imgs)
            c_h = int(height * 0.18) if is_vert else int(height * 0.28)
            card_y = int(height * 0.52) if is_vert else int(height * 0.45)
            
            for idx, s_img in enumerate(sub_imgs):
                x_pos = 40 + idx * (c_w + 10)
                card = crop_fit(s_img, c_w, c_h)
                canvas.paste(card, (x_pos, card_y))
                
        draw = ImageDraw.Draw(canvas)
        b_top = int(height * 0.75)
        draw.rectangle([(40, b_top), (width - 40, b_top + 180)], fill=(0, 120, 235, 230))
        font = ImageFont.load_default()
        draw.text((60, b_top + 30), title, fill=(255, 255, 255), font=font)
        draw.text((60, 40), f"[{badge}]", fill=(255, 215, 0), font=font)
        return canvas

    # Layout 3: Black Borders Cinematic Split
    def generate_style_3(images, title, badge, width, height, is_vert):
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        num = len(images)
        border_px = 12
        if is_vert:
            sh = (height - (border_px * (num - 1))) // num
            for idx, img in enumerate(images):
                y_pos = idx * (sh + border_px)
                canvas.paste(crop_fit(img, width, sh), (0, y_pos))
        else:
            sw = (width - (border_px * (num - 1))) // num
            for idx, img in enumerate(images):
                x_pos = idx * (sw + border_px)
                canvas.paste(crop_fit(img, sw, height), (x_pos, 0))
                
        draw = ImageDraw.Draw(canvas)
        b_top = int(height * 0.68)
        draw.rectangle([(30, b_top), (width - 30, b_top + 200)], fill=(20, 20, 20, 230))
        draw.rectangle([(30, b_top), (width - 30, b_top + 8)], fill=(255, 215, 0, 255)) # Yellow accent line
        
        font = ImageFont.load_default()
        draw.text((50, b_top + 40), title, fill=(255, 255, 255), font=font)
        draw.text((50, 40), f"[{badge}]", fill=(255, 215, 0), font=font)
        return canvas

    # Layout 4: Center Banner Highlight
    def generate_style_4(images, title, badge, width, height, is_vert):
        canvas = Image.new("RGBA", (width, height), (15, 15, 20, 255))
        num = len(images)
        if is_vert:
            sh = height // num
            for idx, img in enumerate(images):
                canvas.paste(crop_fit(img, width, sh), (0, idx * sh))
        else:
            sw = width // num
            for idx, img in enumerate(images):
                canvas.paste(crop_fit(img, sw, height), (idx * sw, 0))
                
        draw = ImageDraw.Draw(canvas)
        # Center Yellow Banner Box
        b_top = int(height * 0.42)
        draw.rectangle([(0, b_top), (width, b_top + 220)], fill=(255, 200, 0, 230))
        
        font = ImageFont.load_default()
        draw.text((50, b_top + 50), title, fill=(0, 0, 0), font=font)
        draw.text((50, 40), f"[{badge}]", fill=(255, 255, 255), font=font)
        return canvas

    if st.button("🎨 Thumbnail ဒီဇိုင်း ၄ မျိုး စလုံး ဖန်တီးမည်"):
        if uploaded_files:
            imgs = [Image.open(f).convert("RGBA") for f in uploaded_files[:4]]
            is_vert = "9:16" in format_type
            w, h = (1080, 1920) if is_vert else (1280, 720)
            
            with st.spinner("ဒီဇိုင်း ၄ မျိုးကို ဖန်တီးပေးနေပါသည်။ ခဏစောင့်ပါ..."):
                res1 = generate_style_1(imgs, title_text, badge_text, w, h, is_vert)
                res2 = generate_style_2(imgs, title_text, badge_text, w, h, is_vert)
                res3 = generate_style_3(imgs, title_text, badge_text, w, h, is_vert)
                res4 = generate_style_4(imgs, title_text, badge_text, w, h, is_vert)
                
                styles = [
                    ("ဒီဇိုင်း ၁ - Classic Split Grid", res1, "thumbnail_v1.jpg"),
                    ("ဒီဇိုင်း ၂ - Hero Main + Sub Cards", res2, "thumbnail_v2.jpg"),
                    ("ဒီဇိုင်း ၃ - Cinematic Black Border", res3, "thumbnail_v3.jpg"),
                    ("ဒီဇိုင်း ၄ - Center Highlight Banner", res4, "thumbnail_v4.jpg")
                ]
                
                st.success("✨ ဒီဇိုင်း ၄ မျိုးစလုံး ထွက်ရှိလာပါပြီ! ကြိုက်နှစ်သက်ရာကို ရွေးချယ် ဒေါင်းလုဒ်ဆွဲပါ -")
                
                for title_name, img_obj, file_name in styles:
                    st.markdown(f"#### {title_name}")
                    buf = io.BytesIO()
                    img_obj.convert("RGB").save(buf, format="JPEG", quality=95)
                    byte_im = buf.getvalue()
                    
                    st.image(byte_im, caption=title_name, use_container_width=True)
                    st.download_button(f"📥 Download {title_name} (.jpg)", data=byte_im, file_name=file_name, mime="image/jpeg")
                    st.markdown("---")
        else:
            st.error("ကျေးဇူးပြု၍ Movie Scene ပုံ ၂ ပုံမှ ၄ ပုံအထိ တင်ပေးပါ။")
