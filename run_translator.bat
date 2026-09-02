@echo off
chcp 65001 > nul
title Universal File & Text Translator

echo ============================================================
echo       STARTING UNIVERSAL FILE & TEXT TRANSLATOR
echo ============================================================
echo.

python -c "import deep_translator" 2>nul
if %errorlevel% neq 0 (
    echo [Info] Installing required packages...
    pip install --break-system-packages -r requirements.txt
    echo.
)

echo Launching graphical interface...
python translator_app.py
pause
