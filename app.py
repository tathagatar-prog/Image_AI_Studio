import streamlit as st
from PIL import Image
import numpy as np
import io
import os
from pathlib import Path

from modules.compositor import (
    process_image,
    process_video,
    remove_background,
    get_video_info
)

st.set_page_config(page_title="ALPHIDER AI STUDIO", page_icon="🏍️", layout="wide")

BASE = Path(__file__).parent
OUT = BASE / "output"
OUT.mkdir(exist_ok=True)

st.markdown("""
<style>
.main {background: #10131b;}
.block-container {padding-top: 1.5rem; max-width: 1400px;}
.hero {padding: 22px 26px; border-radius: 18px; background: linear-gradient(120deg,#161c2b,#242b3e); border:1px solid #38435b;}
.hero h1 {margin:0;color:#fff;font-size:2.1rem;letter-spacing:1px;}
.hero p {color:#c6cee0;margin:6px 0 0 0;}
.small-note {color:#aeb8ca;font-size:.88rem;}
</style>
<div class="hero">
<h1>🏍️ ALPHIDER AI STUDIO</h1>
<p>Cartoon + Live Action Compositing Studio · Local Python Edition</p>
</div>
""", unsafe_allow_html=True)

st.write("")
with st.sidebar:
    st.header("⚙️ Studio Settings")
    placement = st.selectbox("Character placement", ["Automatic scene placement", "Lower-left", "Lower-centre", "Lower-right"])
    scale_pct = st.slider("Character size", 10, 90, 38, 1)
    shadow = st.checkbox("Generate ground shadow", True)
    match_light = st.checkbox("Match scene brightness", True)
    motion = st.checkbox("Add subtle scene-responsive movement (video)", True)
    bg_remove = st.checkbox("Remove character background if needed", False)
    st.caption("Tip: a transparent PNG gives the cleanest result.")
    st.divider()
    st.caption("All processing runs locally on your computer.")

tab_photo, tab_video, tab_help = st.tabs(["🖼️ Photo Studio", "🎬 Video Studio", "📘 Guide"])

def load_character(upload, remove_bg):
    img = Image.open(upload).convert("RGBA")
    if remove_bg and img.getextrema()[3] == (255, 255):
        img = remove_background(img)
    return img

with tab_photo:
    left, right = st.columns([1, 1])
    with left:
        st.subheader("1. Upload your real photograph")
        photo_file = st.file_uploader("Background photograph", type=["png","jpg","jpeg"], key="photo_bg")
        st.subheader("2. Upload your cartoon character")
        char_file = st.file_uploader("Character image (transparent PNG recommended)", type=["png","webp","jpg","jpeg"], key="photo_char")
        if char_file:
            try:
                character_preview = load_character(char_file, bg_remove)
                st.image(character_preview, caption="Character preview", width=220)
            except Exception as e:
                st.error(f"Could not load character: {e}")
    with right:
        st.subheader("3. Generate composite")
        st.write("The automatic mode estimates a suitable ground/contact position from the lower part of the scene.")
        if st.button("✨ COMPOSITE PHOTO", type="primary", use_container_width=True):
            if not photo_file or not char_file:
                st.warning("Please upload both a background photograph and a character.")
            else:
                try:
                    bg = Image.open(photo_file).convert("RGB")
                    char = load_character(char_file, bg_remove)
                    with st.spinner("Analysing scene and compositing character..."):
                        result = process_image(
                            bg, char, placement=placement, scale_pct=scale_pct,
                            add_shadow=shadow, match_light=match_light
                        )
                    st.session_state["photo_result"] = result
                    st.success("Photo composite created.")
                except Exception as e:
                    st.exception(e)
        if "photo_result" in st.session_state:
            result = st.session_state["photo_result"]
            st.image(result, caption="ALPHIDER AI Studio — output", use_container_width=True)
            buf = io.BytesIO()
            result.save(buf, format="PNG")
            st.download_button("⬇️ Download composite PNG", buf.getvalue(), "alphider_composite.png", "image/png", use_container_width=True)

with tab_video:
    st.subheader("🎬 Video compositing")
    st.info("Upload a video and a transparent character PNG. The first version estimates a stable ground anchor from the opening frame, then keeps the character grounded while adding subtle procedural motion.")
    video_file = st.file_uploader("Background video", type=["mp4","mov","avi","mkv"], key="video_bg")
    video_char_file = st.file_uploader("Cartoon character (transparent PNG recommended)", type=["png","webp","jpg","jpeg"], key="video_char")
    if video_file:
        st.video(video_file)
        try:
            info = get_video_info(video_file)
            st.caption(f"Input: {info['width']}×{info['height']} · {info['fps']:.1f} FPS · {info['duration']:.1f} seconds")
        except Exception:
            pass
    if st.button("🚀 GENERATE CARTOON VIDEO", type="primary", use_container_width=True):
        if not video_file or not video_char_file:
            st.warning("Please upload both a video and a character image.")
        else:
            try:
                char = load_character(video_char_file, bg_remove)
                input_path = OUT / "uploaded_background_video"
                suffix = Path(video_file.name).suffix or ".mp4"
                input_path = input_path.with_suffix(suffix)
                input_path.write_bytes(video_file.getvalue())
                output_path = OUT / "alphider_ai_video.mp4"
                progress = st.progress(0)
                status = st.empty()
                def update(p, msg):
                    progress.progress(min(100, int(p * 100)))
                    status.write(msg)
                with st.spinner("Processing video frames. Longer videos take more time..."):
                    result_path = process_video(
                        str(input_path), char, str(output_path),
                        placement=placement, scale_pct=scale_pct,
                        add_shadow=shadow, match_light=match_light,
                        animate=motion, progress_callback=update
                    )
                st.success("Your composited video is ready!")
                st.video(result_path)
                data = Path(result_path).read_bytes()
                st.download_button("⬇️ Download MP4 video", data, "alphider_ai_video.mp4", "video/mp4", use_container_width=True)
            except Exception as e:
                st.exception(e)

with tab_help:
    st.subheader("How to get the best result")
    st.markdown("""
1. **Prepare your character:** use a full-body PNG with a transparent background. Keep the feet/wheels visible.
2. **Upload a clear background:** roads, pavements and open spaces work best.
3. **Choose placement:** automatic placement is a lower-scene ground-contact estimate. Use the left/centre/right choices if needed.
4. **Generate:** the app blends the character, adds a soft contact shadow and optionally adjusts brightness.
5. **Video:** the character stays anchored to the scene using the opening-frame estimate. Subtle bobbing simulates idle motion.

### Current version limitations
- It does not create new skeletal poses from one still image.
- Automatic placement is a computer-vision heuristic, not guaranteed semantic ground detection.
- The video character anchor is stable rather than full 3D camera tracking.
- Occlusion by passing cars/people is not yet automatically reconstructed.
- For realistic walking/riding, provide a transparent animated GIF/WebP or a sequence of character frames in a future animation module.
""")
    st.subheader("Recommended character asset")
    st.markdown("- Transparent PNG, full body, front or 3/4 view.\n- Character feet should be near the bottom edge.\n- For a scooter/rider, use the complete rider-and-scooter image as one character asset.")
    st.subheader("Troubleshooting")
    st.markdown("- If FFmpeg is not found, install FFmpeg and add it to PATH.\n- If background removal is enabled, the first run may download the rembg model.\n- If the character looks too large, reduce Character size.")
