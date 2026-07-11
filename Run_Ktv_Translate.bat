@echo off
chcp 65001 >nul
echo Starting Ktv Translate...
cd /d "%~dp0"
call venv\Scripts\activate
python app.py
pause
