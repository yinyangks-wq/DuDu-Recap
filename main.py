import asyncio
import io
import edge_tts
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import streamlit as st

# Streamlit Page Setup
st.set_page_config(
    page_title="AI Video Creator Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Dark Theme Styling
st.markdown(
    """
    <style>
    .stApp { background-color: #0d0f17; color: #ffffff; }
    .tool-card {
        background-color: #161b26;
        border: 1px solid #232a3b;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .tool-info { display: flex; align-items: center; gap: 16px; }
    .tool-icon {
        width: 44px; height: 44px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center; font-size: 20px;
    }
    .tool-title { font-size: 16px; font-weight: 600; color: #ffffff; margin: 0; }
    .tool-desc { font-size: 12px; color: #8b949e; margin: 2px 0 0 0; }
    .section-title { font-size: 14px; font-weight: 600; color: #6e7681; margin: 20px 0 10px 0; text-transform: uppercase; }
    </style>
""",
    unsafe_allow_html=True,
)

# Session State for Menu Switching
if "current_page" not in st.session_state:
  st.session_state["current_page"] = "🏠 Home Dashboard"


def navigate_to(page_name):
  st.session_state["current_page"] = page_name


# Sidebar Menu Navigation
st.sidebar.title("⚡ Tool Suite")
selected_tool = st.sidebar.radio(
    "Select Tool:",
    [
        "🏠 Home Dashboard",
        "⚡ One Click Recap",
        "🎙️ AI Voice & Generate SRT",
        "🖼️ Thumbnail Person & Poster",
        "🌐 Translate Content",
    ],
    index=[
        "🏠 Home Dashboard",
        "⚡ One Click Recap",
        "🎙️ AI Voice & Generate SRT",
        "🖼️ Thumbnail Person & Poster",
        "🌐 Translate Content",
    ].index(st.session_state["current_page"]),
)

# Sync sidebar with session state
st.session_state["current_page"] = selected_tool

# ==========================================
# 🏠 HOME DASHBOARD UI
# ==========================================
if st.session_state["current_page"] == "🏠 Home Dashboard":
  st.title("Customize Home")
  st.caption("Select a tool from below or use the sidebar menu to get started.")

  st.markdown(
      '<div class="section-title">Pinned Tools</div>', unsafe_allow_html=True
  )

  # Tool 1: One Click Recap
  col1, col2 = st.columns([5, 1])
  with col1:
    st.markdown(
        """<div class="tool-card"><div class="tool-info">
        <div class="tool-icon" style="background-color: #2e1065; color: #a855f7;">⚡</div>
        <div><p class="tool-title">One Click Recap</p><p class="tool-desc">Instantly recap any movie or video script</p></div>
        </div></div>""",
        unsafe_allow_html=True,
    )
  with col2:
    if st.button("Launch", key="h_recap"):
      navigate_to("⚡ One Click Recap")
      st.rerun()

  # Tool 2: AI Voice & SRT
  col1, col2 = st.columns([5, 1])
  with col1:
    st.markdown(
        """<div class="tool-card"><div class="tool-info">
        <div class="tool-icon" style="background-color: #1e1b4b; color: #6366f1;">🎙️</div>
        <div><p class="tool-title">AI Voice & Generate SRT</p><p class="tool-desc">Convert script to audio and synced .srt subtitles</p></div>
        </div></div>""",
        unsafe_allow_html=True,
    )
  with col2:
    if st.button("Launch", key="h_voice"):
      navigate_to("🎙️ AI Voice & Generate SRT")
      st.rerun()

  st.markdown(
      '<div class="section-title">More Tools</div>', unsafe_allow_html=True
  )

  # Tool 3: Poster & Thumbnail
  col1, col2 = st.columns([5, 1])
  with col1:
    st.markdown(
        """<div class="tool-card"><div class="tool-info">
        <div class="tool-icon" style="background-color: #064e3b; color: #10b981;">🖼️</div>
        <div><p class="tool-title">Thumbnail Person & Poster</p><p class="tool-desc">Create multi-layer poster compositions and cutouts</p></div>
        </div></div>""",
        unsafe_allow_html=True,
    )
  with col2:
    if st.button("Launch", key="h_poster"):
      navigate_to("🖼️ Thumbnail Person & Poster")
      st.rerun()

  # Tool 4: Translate Content
  col1, col2 = st.columns([5, 1])
  with col1:
    st.markdown(
        """<div class="tool-card"><div class="tool-info">
        <div class="tool-icon" style="background-color: #312e81; color: #818cf8;">🌐</div>
        <div><p class="tool-title">Translate Content</p><p class="tool-desc">Translate scripts to Burmese or other languages</p></div>
        </div></div>""",
        unsafe_allow_html=True,
    )
  with col2:
    if st.button("Launch", key="h_trans"):
      navigate_to("🌐 Translate Content")
      st.rerun()

# ==========================================
# ⚡ ONE CLICK RECAP FUNCTION
# ==========================================
elif st.session_state["current_page"] == "⚡ One Click Recap":
  st.subheader("⚡ One Click Movie/Anime Recap Generator")

  api_key = st.text_input("Gemini API Key ထည့်ပါ:", type="password")
  raw_story = st.text_area(
      "ဇာတ်လမ်း အကျဉ်း သို့မဟုတ် Plot Detail များ ထည့်ပါ:", height=200
  )

  if st.button("🚀 Generate Recap Script"):
    if api_key and raw_story:
      try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            "You are a professional movie recap creator. Write an engaging"
            " movie recap script in Burmese language based on the following"
            f" text:\n{raw_story}"
        )

        with st.spinner("AI Script ရေးသားနေပါသည်..."):
          response = model.generate_content(prompt)
          st.success("✨ Script ရရှိပါပြီ!")
          st.text_area("Generated Recap Script:", response.text, height=250)
      except Exception as e:
        st.error(f"Error occurred: {e}")
    else:
      st.warning("API Key နှင့် Plot စာသား ဖြည့်သွင်းပေးပါ။")

# ==========================================
# 🎙️ AI VOICE & SRT GENERATOR FUNCTION
# ==========================================
elif st.session_state["current_page"] == "🎙️ AI Voice & Generate SRT":
  st.subheader("🎙️ AI Voice & SRT Subtitle Generator")

  script_input = st.text_area("Script စာသား ရေးထည့်ပါ:", height=180)
  voice_choice = st.selectbox(
      "အသံ ရွေးပါ:",
      [("မြန်မာ - Nilar (Female)", "my-MM-NilarNeural"), ("မြန်မာ - Thiha (Male)", "my-MM-ThihaNeural")],
      format_func=lambda x: x[0],
  )


  def make_srt(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    srt = ""
    t = 0
    for i, line in enumerate(lines, 1):
      dur = max(2, len(line) * 0.25)
      end = t + dur

      def fmt(s):
        h, m, sec, ms = (
            int(s // 3600),
            int((s % 3600) // 60),
            int(s % 60),
            int((s - int(s)) * 1000),
        )
        return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

      srt += f"{i}\n{fmt(t)} --> {fmt(end)}\n{line}\n\n"
      t = end
    return srt


  async def generate_speech(text, v_code):
    comm = edge_tts.Communicate(text, v_code)
    await comm.save("voice.mp3")


  if st.button("🚀 Audio & SRT ထုတ်ယူမည်"):
    if script_input.strip():
      with st.spinner("ဖန်တီးနေပါသည်..."):
        asyncio.run(generate_speech(script_input, voice_choice[1]))
        srt_data = make_srt(script_input)

        with open("voice.mp3", "rb") as f:
          audio_data = f.read()

        st.audio(audio_data, format="audio/mp3")

        c1, c2 = st.columns(2)
        c1.download_button(
            "📥 Download Audio (.mp3)",
            audio_data,
            "recap_audio.mp3",
            "audio/mp3",
        )
        c2.download_button(
            "📥 Download Subtitle (.srt)", srt_data, "subtitles.srt", "text/plain"
        )
    else:
      st.warning("Script ထည့်ပေးပါ။")

# ==========================================
# 🖼️ THUMBNAIL PERSON & POSTER COMPOSITOR
# ==========================================
elif st.session_state["current_page"] == "🖼️ Thumbnail Person & Poster":
  st.subheader("🖼️ Multi-layer Poster & Concept Art Compositor")

  col_inputs, col_preview = st.columns([1, 2])

  with col_inputs:
    bg_img = st.file_uploader("1. Background Image", type=["jpg", "png"])
    hero_img = st.file_uploader(
        "2. Hero Person PNG (Transparent)", type=["png"]
    )
    item_img = st.file_uploader("3. Magic Item/Jar PNG", type=["png"])

    p_title = st.text_input("Title Text", "MAGIC JAR SHOP")
    h_x = st.slider("Hero Position X", 0, 1000, 350)
    h_y = st.slider("Hero Position Y", 0, 1000, 100)
    h_scale = st.slider("Hero Scale (%)", 20, 200, 100)

  def draw_poster():
    cw, ch = 1280, 720
    canvas = (
        Image.open(bg_img).convert("RGBA").resize((cw, ch))
        if bg_img
        else Image.new("RGBA", (cw, ch), (20, 10, 35, 255))
    )

    if hero_img:
      h_pic = Image.open(hero_img).convert("RGBA")
      ow, oh = h_pic.size
      nw, nh = int(ow * (h_scale / 100.0)), int(oh * (h_scale / 100.0))
      canvas.paste(
          h_pic.resize((nw, nh)), (h_x, h_y), h_pic.resize((nw, nh))
      )

    draw = ImageDraw.Draw(canvas)
    draw.rectangle(
        [(50, 40), (500, 120)],
        fill=(15, 10, 25, 220),
        outline=(212, 175, 55),
        width=3,
    )
    draw.text((70, 60), p_title, fill=(255, 215, 0))
    return canvas

  with col_preview:
    poster = draw_poster()
    buf = io.BytesIO()
    poster.convert("RGB").save(buf, format="JPEG", quality=95)
    st.image(buf.getvalue(), use_container_width=True)
    st.download_button("📥 Download Poster", buf.getvalue(), "poster.jpg", "image/jpeg")

# ==========================================
# 🌐 TRANSLATE CONTENT FUNCTION
# ==========================================
elif st.session_state["current_page"] == "🌐 Translate Content":
  st.subheader("🌐 Translate Content")

  api_key_t = st.text_input("Gemini API Key:", type="password")
  src_text = st.text_area("ဘာသာပြန်လိုသော စာသားများ ရေးထည့်ပါ:", height=180)
  target_lang = st.selectbox(
      "ပြန်ဆိုချင်သည့် ဘာသာစကား:", ["Burmese (မြန်မာ)", "English"]
  )

  if st.button("🚀 Translate Text"):
    if api_key_t and src_text:
      try:
        genai.configure(api_key=api_key_t)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Translate the following content into {target_lang}:\n\n{src_text}"

        with st.spinner("Translating..."):
          res = model.generate_content(prompt)
          st.success("Translated Output:")
          st.text_area("Result:", res.text, height=200)
      except Exception as e:
        st.error(f"Error: {e}")
    else:
      st.warning("API Key နှင့် စာသား ရေးပေးပါ။")
