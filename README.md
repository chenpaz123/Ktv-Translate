# Ktv Translate - AI Subtitles

Ktv Translate is a standalone, blazing-fast local application that translates English SRT subtitle files into Hebrew entirely on your own machine. It is specifically optimized to utilize NVIDIA GPUs (CUDA) via the highly efficient CTranslate2 inference engine, allowing you to translate entire seasons in seconds.

## Features
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
   - Install all required dependencies (`ctranslate2`, `transformers`, `customtkinter`, `pysrt`, NVIDIA DLLs, etc.).

## Usage

1. Double-click `Run_Ktv_Translate.bat` to launch the application.
2. Click **בחר קבצי SRT לתרגום** (Select SRT files for translation).
3. Select one or more English `.srt` files.
4. The translated files will be automatically saved in the same directory as the original files, with `_hebrew.srt` appended to the name.

## Requirements
- Python 3.8 or higher.
- (Optional but Highly Recommended) An NVIDIA GPU for CUDA acceleration. If no compatible GPU is found, the application will fallback to CPU translation seamlessly.
