# ALPHIDER AI STUDIO

A local Streamlit + Python prototype for compositing a transparent cartoon character into real photographs and videos.

## Features in this version
- Photo compositing: JPG, JPEG, PNG.
- Video compositing: MP4, MOV, AVI, MKV (codec support depends on OpenCV).
- Transparent PNG character input.
- Optional AI background removal with `rembg`.
- Automatic lower-scene placement heuristic, plus left/centre/right placement choices.
- Soft contact shadow and approximate brightness matching.
- Procedural subtle bobbing for video output.
- Download PNG and MP4 results.

## Important scope notes
This is a working first-stage compositing studio, not a fully autonomous generative video model. Automatic placement estimates a plausible ground-contact point from image edge density in the lower frame. It cannot reliably identify every road, sidewalk, wall, or object. Video placement is anchored using the opening-frame heuristic; it does not yet perform full camera tracking, 3D reconstruction, per-frame semantic segmentation, or automatic foreground occlusion. A single still PNG cannot produce genuine walking/riding poses; those require animation frames or a rigged character.

## Requirements
- Windows 10/11, macOS, or Linux.
- Python 3.11 recommended.
- 8 GB RAM minimum; 16 GB recommended.
- FFmpeg is recommended for broad codec compatibility, although the app uses OpenCV's video reader/writer.

## Windows installation
1. Extract `ALPHIDER_AI_STUDIO.zip`.
2. Open the extracted folder in VS Code.
3. Open Terminal > New Terminal.
4. Run:
   ```powershell
   py -3.11 -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   streamlit run app.py
   ```
5. Open the local URL shown in the terminal, usually `http://localhost:8501`.

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### One-click Windows launch
Double-click `run_windows.bat`. It creates a virtual environment, installs dependencies, and launches the app.

## macOS / Linux
```bash
chmod +x run_mac_linux.sh
./run_mac_linux.sh
```

## How to use
### Photo
1. Open **Photo Studio**.
2. Upload a background photo.
3. Upload your character PNG (transparent background strongly recommended).
4. Choose automatic placement or a lower-left/centre/right position.
5. Adjust character size and shadow/light options.
6. Click **COMPOSITE PHOTO**, then download the PNG.

### Video
1. Open **Video Studio**.
2. Upload a background video and transparent character PNG.
3. Choose placement and size.
4. Click **GENERATE CARTOON VIDEO**.
5. Wait for frame rendering, preview and download the MP4.

## Character preparation
Best results:
- PNG with transparent background (RGBA).
- Full body / full scooter visible.
- Feet or wheels close to the bottom edge.
- Avoid a character crop with large empty margins.
- For rider-on-scooter scenes, use one combined transparent rider + scooter image.

If your character has a solid background, enable **Remove character background if needed**. `rembg` may download a model on first use. Background removal works best when the subject is clearly separated from the background.

## Troubleshooting
- **`py` is not recognized:** install Python 3.11 from python.org and enable “Add Python to PATH”.
- **`No module named cv2`:** activate `.venv`, then run `pip install -r requirements.txt`.
- **Video cannot be opened:** try MP4 (H.264) or convert the source video to MP4 using FFmpeg.
- **Output video is black / unsupported:** install FFmpeg and use an H.264 MP4 input. OpenCV codec support varies by platform.
- **Slow rendering:** shorten the video, lower its resolution, or use a shorter clip.
- **Character background appears:** use a transparent PNG or enable background removal.

## Folder structure
```text
ALPHIDER_AI_STUDIO/
├── app.py
├── requirements.txt
├── README.md
├── run_windows.bat
├── run_mac_linux.sh
├── modules/
│   ├── __init__.py
│   └── compositor.py
├── assets/
│   └── characters/
├── output/
└── temp/
```

## Roadmap
- SAM2-based semantic ground and object segmentation.
- Video object tracking and camera-motion compensation.
- Per-frame depth-aware placement and occlusion.
- Animated PNG/GIF/WebP frame sequences and character rig support.
- Realistic contact lighting, colour grading and motion blur.
