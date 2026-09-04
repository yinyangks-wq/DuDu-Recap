import asyncio
import io
import edge_tts
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import streamlit as st

st.set_page_config(
    page_title="Movie Recap All-in-One Suite", page_icon="🎬", layout="wide"
)

st.title("🎬 Movie Recap All-in-One Automation Suite")
st.write(
    "Recap Script မှ Audio/SRT ထုတ်ခြင်း၊ Multi-Image Collage Thumbnails ဖန်တီးခြင်းနှင့်"
    " Advanced Layered Poster များ ပြုလုပ်နိုင်သည့် Tool"
)

# Tab ၃ ခု ခွဲခြားထားခြင်း
tab1, tab2, tab3 = st.tabs([
    "🎙️ Voice & Subtitle",
    "🖼️ Multi-Thumbnail Variations",
    "🧙‍♂️ Advanced Poster Compositor",
])

# ==========================================
# TAB 1: VOICE & SUBTITLE GENERATOR
# ==========================================
with tab1:
  st.subheader("🎙️ Voiceover (.mp3) & Subtitle (.srt) Generator")
  script_text = st.text_area(
      "Recap Script စာသားများကို ဒီမှာ Paste လုပ်ပါ:", height=200
  )

  voice_option = st.selectbox(
      "အသံအမျိုးအစား ရွေးပါ:",
      [
          ("မြန်မာ - Nilar (Female)", "my-MM-NilarNeural"),
          ("မြန်မာ - Thiha (Male)", "my-MM-ThihaNeural"),
          ("English - Christopher (Male)", "en-US-ChristopherNeural"),
          ("English - Ava (Female)", "en-US-AvaNeural"),
      ],
      format_func=lambda x: x[0],
  )


  def text_to_srt(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
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

      srt_content += (
          f"{i}\n{format_time(start_time)} -->"
          f" {format_time(end_time)}\n{line}\n\n"
      )
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
          st.download_button(
              "📥 Download Audio (.mp3)",
              data=audio_bytes,
              file_name="recap_voice.mp3",
              mime="audio/mp3",
          )
        with col2:
          st.download_button(
              "📥 Download Subtitle (.srt)",
              data=srt_data,
              file_name="recap_subtitles.srt",
              mime="text/plain",
          )
    else:
      st.error("Script စာသား ထည့်ပေးပါ။")

# ==========================================
# TAB 2: MULTI-IMAGE THUMBNAIL VARIATIONS
# ==========================================
with tab2:
  st.subheader("🖼️ Collage Thumbnail Generator (၄ မျိုး)")

  uploaded_files = st.file_uploader(
      "Movie Scene ပုံများ (၂ ပုံမှ ၄ ပုံအထိ ရွေးပေးပါ):",
      type=["jpg", "jpeg", "png"],
      accept_multiple_files=True,
  )

  title_text = st.text_input(
      "ခေါင်းစဉ် စာသား (Hook Title):", "ဒီဇာတ်လမ်းက တကယ်ရူးသွပ်စရာပဲ!"
  )
  badge_text = st.text_input("အပေါ်တန်း စာသား (Badge Text):", "MOVIE RECAP")
  format_type = st.radio(
      "Format ရွေးပါ:",
      ["TikTok / Reels (9:16)", "YouTube (16:9)"],
      horizontal=True,
  )


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
    draw.rectangle(
        [(40, b_top), (width - 40, b_top + 220)], fill=(230, 25, 50, 220)
    )
    font = ImageFont.load_default()
    draw.text((60, b_top + 40), title, fill=(255, 255, 255), font=font)
    draw.text((60, 40), f"[{badge}]", fill=(255, 215, 0), font=font)
    return canvas


  def generate_style_2(images, title, badge, width, height, is_vert):
    canvas = Image.new("RGBA", (width, height), (15, 15, 20, 255))
    hero = crop_fit(images[0], width, height)
    canvas.paste(hero, (0, 0))

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d_overlay = ImageDraw.Draw(overlay)
    for y in range(int(height * 0.35), height):
      alpha = int(230 * ((y - height * 0.35) / (height * 0.65)))
      d_overlay.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
    canvas = Image.alpha_composite(canvas, overlay)

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
    draw.rectangle(
        [(40, b_top), (width - 40, b_top + 180)], fill=(0, 120, 235, 230)
    )
    font = ImageFont.load_default()
    draw.text((60, b_top + 30), title, fill=(255, 255, 255), font=font)
    draw.text((60, 40), f"[{badge}]", fill=(255, 215, 0), font=font)
    return canvas


  if st.button("🎨 Thumbnail ဒီဇိုင်းများ ဖန်တီးမည်"):
    if uploaded_files:
      imgs = [Image.open(f).convert("RGBA") for f in uploaded_files[:4]]
      is_vert = "9:16" in format_type
      w, h = (1080, 1920) if is_vert else (1280, 720)

      res1 = generate_style_1(imgs, title_text, badge_text, w, h, is_vert)
      res2 = generate_style_2(imgs, title_text, badge_text, w, h, is_vert)

      col_a, col_b = st.columns(2)
      with col_a:
        st.markdown("#### ဒီဇိုင်း ၁ - Classic Split Grid")
        buf1 = io.BytesIO()
        res1.convert("RGB").save(buf1, format="JPEG", quality=95)
        st.image(buf1.getvalue(), use_container_width=True)
        st.download_button(
            "📥 Download Style 1",
            data=buf1.getvalue(),
            file_name="thumbnail_v1.jpg",
            mime="image/jpeg",
        )

      with col_b:
        st.markdown("#### ဒီဇိုင်း ၂ - Hero Main + Sub Cards")
        buf2 = io.BytesIO()
        res2.convert("RGB").save(buf2, format="JPEG", quality=95)
        st.image(buf2.getvalue(), use_container_width=True)
        st.download_button(
            "📥 Download Style 2",
            data=buf2.getvalue(),
            file_name="thumbnail_v2.jpg",
            mime="image/jpeg",
        )
    else:
      st.error("ကျေးဇူးပြု၍ Movie Scene ပုံများ တင်ပေးပါ။")

# ==========================================
# TAB 3: ADVANCED POSTER COMPOSITOR (LAYERED)
# ==========================================
with tab3:
  st.subheader("🧙‍♂️ Advanced Poster Compositor (Multi-Layer Cutouts)")
  st.write(
      "Background, Hero Character, Item (Magic Jar) နှင့် Text Banner များကို"
      " Layer အလိုက် စီစဉ်ပေးနိုင်သော Tool"
  )

  col_ctrl, col_prev = st.columns([1, 2])

  with col_ctrl:
    bg_f = st.file_uploader(
        "၁။ Background Image", type=["jpg", "png"], key="p_bg"
    )
    side_f = st.file_uploader(
        "၂။ Side Characters PNG (Transparent)", type=["png"], key="p_side"
    )
    hero_f = st.file_uploader(
        "၃။ Main Hero PNG (Transparent)", type=["png"], key="p_hero"
    )
    item_f = st.file_uploader(
        "၄။ Magic Item / Jar PNG", type=["png"], key="p_item"
    )

    p_title = st.text_input("Main Title", "MAGIC JAR SHOP")
    p_sub = st.text_input("Subtitle", "100,000 GOLD SOUL COINS")
    p_badge = st.text_input("Badge Text", "x10 LUCKY JAR")

    hero_x = st.slider("Hero Position X", 0, 1000, 350)
    hero_y = st.slider("Hero Position Y", 0, 1000, 100)
    hero_scale = st.slider("Hero Scale (%)", 20, 200, 100)

    item_x = st.slider("Item Position X", 0, 1000, 450)
    item_y = st.slider("Item Position Y", 0, 1000, 400)
    item_scale = st.slider("Item Scale (%)", 10, 150, 60)


  def generate_layered_poster():
    cw, ch = 1280, 720
    if bg_f:
      canvas = Image.open(bg_f).convert("RGBA").resize((cw, ch))
    else:
      canvas = Image.new("RGBA", (cw, ch), (20, 10, 35, 255))

    # Side characters
    if side_f:
      s_img = Image.open(side_f).convert("RGBA").resize((cw, ch))
      canvas.paste(s_img, (0, 0), s_img)

    # Hero character
    if hero_f:
      h_img = Image.open(hero_f).convert("RGBA")
      ow, oh = h_img.size
      nw, nh = int(ow * (hero_scale / 100.0)), int(oh * (hero_scale / 100.0))
      canvas.paste(h_img.resize((nw, nh)), (hero_x, hero_y), h_img.resize((nw, nh)))

    # Item with Glow Effect
    if item_f:
      i_img = Image.open(item_f).convert("RGBA")
      ow, oh = i_img.size
      nw, nh = int(ow * (item_scale / 100.0)), int(oh * (item_scale / 100.0))
      resized_item = i_img.resize((nw, nh))

      glow = resized_item.filter(ImageFilter.GaussianBlur(12))
      glow = ImageEnhance.Brightness(glow).enhance(2.0)

      canvas.paste(glow, (item_x - 5, item_y - 5), glow)
      canvas.paste(resized_item, (item_x, item_y), resized_item)

    # Text Banner
    draw = ImageDraw.Draw(canvas)
    draw.rectangle(
        [(50, 40), (520, 140)],
        fill=(15, 10, 25, 220),
        outline=(212, 175, 55),
        width=3,
    )

    font = ImageFont.load_default()
    draw.text((70, 55), p_title, fill=(255, 215, 0), font=font)
    draw.text((70, 90), p_sub, fill=(255, 255, 255), font=font)

    # Item Badge
    draw.rectangle(
        [(item_x, item_y + 120), (item_x + 140, item_y + 155)],
        fill=(200, 30, 30, 230),
        outline=(255, 255, 255),
        width=2,
    )
    draw.text((item_x + 10, item_y + 130), p_badge, fill=(255, 255, 255), font=font)

    return canvas


  with col_prev:
    st.markdown("#### Live Poster Preview")
    poster_result = generate_layered_poster()

    buf_p = io.BytesIO()
    poster_result.convert("RGB").save(buf_p, format="JPEG", quality=95)
    st.image(buf_p.getvalue(), use_container_width=True)

    st.download_button(
        "📥 Download Layered Poster (.jpg)",
        data=buf_p.getvalue(),
        file_name="concept_poster.jpg",
        mime="image/jpeg",
    )
