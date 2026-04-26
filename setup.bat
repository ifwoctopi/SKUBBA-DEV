@echo off
REM Quick setup script for Skin Scanner with AI

echo.
echo ===============================================
echo   Skin Scanner with AI - Setup
echo ===============================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

echo.
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo ===============================================
echo   Setup Instructions Complete
echo ===============================================
echo.
echo Next steps:
echo 1. Install Ollama from https://ollama.ai
echo 2. Pull a model: ollama pull llama2
echo 3. Run the application: python webcam-test.py
echo.
echo For detailed setup, see SETUP_GUIDE.md
echo.
pause
