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
pip install torch transformers pysrt customtkinter sentencepiece sacremoses ctranslate2 nvidia-cublas-cu12 nvidia-cudnn-cu12 ffsubsync

echo.
echo [3/3] Installation Complete!
echo You can now run the app using Run_Ktv_Translate.bat
pause
