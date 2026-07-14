# Ktv Translate - AI Subtitles

Ktv Translate is a standalone, blazing-fast local application that translates English SRT subtitle files into Hebrew entirely on your own machine. It is specifically optimized to utilize NVIDIA GPUs (CUDA) via the highly efficient CTranslate2 inference engine, allowing you to translate entire seasons in seconds.

## Features
- **Auto-Sync to Video**: Automatically detects speech in your video files using `FFsubsync` and perfectly aligns your out-of-sync English subtitles before translating them.
- **100% Offline & Local**: No data is sent to the cloud. Your subtitles stay on your machine.
- **Hardware Acceleration**: Automatically detects and uses your NVIDIA GPU (CUDA) for lightning-fast translation, bypassing PyTorch setup issues.
- **Batch Processing**: Select multiple `.srt` files at once (e.g., an entire season) and it will translate them sequentially.
- **Dedicated Hebrew Model**: Uses `Helsinki-NLP/opus-mt-en-he` explicitly converted to CTranslate2 format for maximum efficiency.
- **Simple UI**: Modern, easy-to-use Dark Mode GUI powered by CustomTkinter.

## Installation

1. Make sure you have **Python** installed on your system.
2. Clone or download this repository.
3. Double-click the `Install_Ktv_Translate.bat` script. This will automatically:
   - Create an isolated Python virtual environment (`venv`).
   - Install all required dependencies (`ctranslate2`, `transformers`, `customtkinter`, `pysrt`, `ffsubsync`, NVIDIA DLLs, etc.).

## Usage

Double-click `Run_Ktv_Translate.bat` to launch the application. You have two options:

### 1. Auto-Sync + Translate (Recommended)
Use this if your downloaded subtitles are out of sync with your video file.
1. Click **סנכרון + תרגום אוטומטי (מומלץ)**.
2. Select your video file (MP4, MKV, etc.).
3. Select the corresponding out-of-sync English `.srt` file.
4. The app will listen to the video, automatically align the timestamps, and then translate it. The output will be saved as `[filename]_synced_hebrew.srt`.

### 2. Translate Only
Use this if your subtitles are already perfectly synchronized.
1. Click **תרגום כתוביות בלבד (ללא סנכרון)**.
2. Select one or more English `.srt` files.
3. The translated files will be automatically saved as `[filename]_hebrew.srt`.

### 3. Extract, Translate & Mux (Embedded Subtitles)
Use this if your video files already contain embedded English subtitles (like MKV files).
1. Click **חילוץ ותרגום כתוביות מובנות מתוך וידאו**.
2. Select one or more video files (Batch processing supported - e.g. an entire season).
3. The app will automatically extract the embedded subtitles, translate them to Hebrew, and generate a new duplicate video file with the Hebrew subtitles natively embedded as the default track.

## Requirements
- Python 3.8 or higher.
- (Optional but Highly Recommended) An NVIDIA GPU for CUDA acceleration. If no compatible GPU is found, the application will fallback to CPU translation seamlessly.
- **FFmpeg**: Required for the Auto-Sync feature to extract audio from videos. It usually comes pre-installed, but if auto-sync fails, ensure FFmpeg is installed and added to your system PATH.

---

## 🤖 AI-Assisted Development
This project is part of an AI development portfolio, showcasing the power of human-AI collaboration in software engineering. The entire codebase, architecture, bug fixing, and optimization were pair-programmed alongside an advanced Agentic AI coding assistant.
