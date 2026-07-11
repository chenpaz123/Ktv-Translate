@echo off
chcp 65001 >nul
echo ===========================================
echo   Ktv Translate - Installation Setup
echo ===========================================
echo.

:: Check for python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python from python.org to use this app.
    pause
    exit /b
)

echo [1/3] Creating Virtual Environment...
if not exist "venv" (
    python -m venv venv
)

echo [2/3] Installing Dependencies...
call venv\Scripts\activate
pip install --upgrade pip
pip install torch transformers pysrt customtkinter sentencepiece sacremoses ctranslate2 nvidia-cublas-cu12 nvidia-cudnn-cu12 ffsubsync python-bidi

echo.
echo [3/4] Downloading Translation Model (NLLB 600M)...
if not exist "nllb-200-600M-ct2" (
    echo This might take a few minutes...
    ct2-transformers-converter --model facebook/nllb-200-distilled-600M --output_dir nllb-200-600M-ct2 --quantization int8
)

echo.
echo [4/4] Installation Complete!
echo You can now run the app using Run_Ktv_Translate.bat
pause
